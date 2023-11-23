## Copyright (c) 2019, 2023 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

""" @package events

This module implements common event callback functions, these are
registered using `events.register_callback()` to be triggered at some point
in the future

"""

from __future__ import division

import logging

import peewee

import censere.events as EVENTS
import censere.models as MODELS
import censere.utils as UTILS
import censere.utils.random as RANDOM
from censere.config import thisApp

from .store import register_callback as register_callback

LOGGER = logging.getLogger("c.e.callbacks")
DEVLOG = logging.getLogger("d.devel")

## A person dies
#
def settler_dies(**kwargs):

    id = None
    name = None

    for k,v in kwargs.items():
        if k == "id":
            id = v
        if k == "name":
            name = v

    if id == None:
        LOGGER.error( "settler_dies event called with no person identifier")
        return

    LOGGER.log( thisApp.NOTICE, "%d.%03d Settler %s (%s) dies ", *UTILS.from_soldays( thisApp.solday ), name, id )

    # Call the instance method to trigger callback handling.
    for c in MODELS.Settler().select().filter( ( MODELS.Settler.settler_id == id ) & ( MODELS.Settler.simulation_id == thisApp.simulation ) ):

        c.death_solday = thisApp.solday

        c.save()

## A person should be born -
# the new person object is created only if mother is still alive
#
def settler_born(**kwargs):

    biological_mother = None
    biological_father = None

    for k,v in kwargs.items():
        if k == "biological_mother":
            biological_mother = v
        if k == "biological_father":
            biological_father = v

    if biological_mother == None or biological_father == None:
        LOGGER.error( "settler_born event called with no biological parents specified")
        return

    father = None
    mother = None

    try:
        father = MODELS.Settler.get( MODELS.Settler.settler_id == str(biological_father) )
        mother = MODELS.Settler.get( MODELS.Settler.settler_id == str(biological_mother) )

    except Exception as e:

        LOGGER.error( '%d.%03d Failed to find parents %s (%s) or %s (%s)', *UTILS.from_soldays( thisApp.solday ), father, str(biological_father), mother, str(biological_mother) )
        return

    # Mother died while pregnant - no child
    if mother.death_solday:
        LOGGER.log( thisApp.NOTICE, '%d.%03d Mother %s died while pregnant.', *UTILS.from_soldays( thisApp.solday ), str(biological_mother) )
        return

    mother.pregnant = False
    mother.save()

    m = MODELS.Martian()

    m.initialize( thisApp.solday )

    m.biological_father = biological_father
    m.biological_mother = biological_mother

    m.family_name = father.family_name


    saved = m.save()

    # create the parent <-> child relationship
    r1 = MODELS.Relationship()

    r1.simulation_id = thisApp.simulation

    r1.relationship_id= RANDOM.id()
    r1.first=m.settler_id
    r1.second=mother.settler_id
    r1.relationship=MODELS.RelationshipEnum.parent
    r1.begin_solday=thisApp.solday

    r1.save()

    r2 = MODELS.Relationship()

    r2.simulation_id = thisApp.simulation

    r2.relationship_id= RANDOM.id()
    r2.first=m.settler_id
    r2.second=father.settler_id
    r2.relationship=MODELS.RelationshipEnum.parent
    r2.begin_solday=thisApp.solday

    r2.save()

    LOGGER.log( thisApp.NOTICE, '%d.%03d Martian %s %s (%s) born', *UTILS.from_soldays( thisApp.solday ), m.first_name, m.family_name, m.settler_id )

    age_at_death = RANDOM.parse_random_value( thisApp.martian_life_expectancy, default_value=1, key_in_earth_years=True)


    register_callback(
        runon=thisApp.solday + age_at_death,
        priority = 20,
        callback_func=EVENTS.settler_dies,
        kwargs= { "simulation": thisApp.simulation, "id" : m.settler_id, "name":"{} {}".format( m.first_name, m.family_name) }
    )

    # Are parents still together ?
    # if so then handle a possible sibling

    parents_relationships = MODELS.Relationship.get(
            (
                ( MODELS.Relationship.first == str(biological_father) ) &
                ( MODELS.Relationship.second == str(biological_mother) )
            ) |
            (
                ( MODELS.Relationship.first == str(biological_mother) ) &
                ( MODELS.Relationship.second == str(biological_father) )
            )
    )

    if parents_relationships.end_solday == 0:

        mothers_age = UTILS.sols_to_age(thisApp.solday - mother.birth_solday)

        r = RANDOM.random()

        # TODO trying to provide some falloff with age - but this is too simple
        # TODO - need to confirm IFV rate - assume best case
        # scenario of freezing eggs before leaving earth
        if (
            mothers_age < 36 and r < 0.7
        ) or (
            mothers_age < 38 and r < 0.2
        ) or (
            mothers_age <= 40 and r < 0.05
        ) or (
            thisApp.use_ivf and ( mothers_age <= 45 and r < 0.4 ) ):


            when = thisApp.solday + RANDOM.parse_random_value( thisApp.sols_between_siblings)

            LOGGER.log( thisApp.NOTICE, '%d.%03d Sibling of %s %s (%s) to be born on %d.%03d',
                *UTILS.from_soldays( thisApp.solday ),
                m.first_name, m.family_name, m.settler_id, *UTILS.from_soldays( when )  )

            register_callback(
                # handle the "cool off" period...
                runon=when,
                priority=20,
                callback_func=EVENTS.settler_born,
                kwargs= {
                    "simulation": thisApp.simulation,
                    "biological_mother" : mother.settler_id,
                    "biological_father": father.settler_id
                }
            )

        else:
            LOGGER.log( thisApp.NOTICE, '%d.%03d No siblings for %s %s (%s)',
                *UTILS.from_soldays( thisApp.solday ),
                m.first_name, m.family_name, m.settler_id )

    else:
        LOGGER.log( thisApp.NOTICE, '%d.%03d Parents of %s %s (%s) are no longer together, no siblings',
                *UTILS.from_soldays( thisApp.solday ),
                m.first_name, m.family_name, m.settler_id )

##
# A new lander arrives with #settlers
#
# TODO handle children (imagine aged 10-18, younger than that might be real world difficult)
def mission_lands(**kwargs):

    settlers = RANDOM.parse_random_value( kwargs['settlers'] )

    # idx is the index of the function for this day to distinguish
    # between multiple missions landing on the same day
    idx = 0
    if "idx" in kwargs:
        idx = kwargs['idx']

    LOGGER.log( thisApp.NOTICE, "%d.%03d Mission landed with %d settlers", *UTILS.from_soldays( thisApp.solday ), settlers )


    for i in range(settlers):

        a = MODELS.Astronaut()

        try:
            a.initialize( thisApp.solday )
        except Exception as e:

            LOGGER.error( 'Failed to initialize new astronaut: %s %s', str(e), str( a) )

            continue

        saved = a.save()

        LOGGER.info( '%d.%03d Astronaut %s %s (%s) landed', *UTILS.from_soldays( thisApp.solday ), a.first_name, a.family_name, a.settler_id )

        # TODO model women outliving men
        # extra fudge `random.randrange(1, 660)` is to avoid the optics of a number of astronauts dying on the day they land
        # don't let death day be before today or they will never die.
        current_age = thisApp.solday - a.birth_solday

        age_at_death = RANDOM.parse_random_value( thisApp.astronaut_life_expectancy, key_in_earth_years=True)

        date_of_death = a.birth_solday + age_at_death

        register_callback(
            runon= max( date_of_death, thisApp.solday + RANDOM.randrange(1, 660)),
            priority=20,
            callback_func=EVENTS.settler_dies,
            kwargs= { "simulation": thisApp.simulation, "id" : a.settler_id, "name":"{} {}".format( a.first_name, a.family_name) }
        )


##
# Break a relationship
#
#
def end_relationship(**kwargs):

    id = kwargs['relationship_id']

    LOGGER.info("%d.%03d Relationship %s ended", *UTILS.from_soldays( thisApp.solday ), id )


    rel = MODELS.Relationship.get( ( MODELS.Relationship.relationship_id == id ) & ( MODELS.Relationship.simulation_id == thisApp.simulation )  )

    rel.end_solday = thisApp.solday

    rel.save()


def commodities_landed(**kwargs):

    resources = []

    if "resources" in kwargs:
        resources = kwargs["resources"]

    if len( resources ) and resources[0] != "":
        thisApp.report_commodity_status = True

    if thisApp.solday < 0:
        LOGGER.log( thisApp.NOTICE, "%d.%03d Mission (Seed) landed with %d resources specifications", *UTILS.from_soldays( thisApp.solday ), len(resources))
    else:
        LOGGER.log( thisApp.NOTICE, "%d.%03d Mission landed with %d resource specifications", *UTILS.from_soldays( thisApp.solday ), len(resources))

    for res in resources:

        if res == "":
            continue

        fields = res.split(" ")

        # examples
        #   count=randint:2,4 supply=electricity availbility=randint:99,100 supplies=gauss:0.4,0.0001 description=RTG",
        #   count=randint:1,3 store=electricity availbility=randint:99,100 initial-capacity=gauss:4.4,0.1 max-capacity=gauss:10,1 equipment=battery",
        count = fields[0].split("=")

        for idx in range(RANDOM.parse_random_value( count[1] ) ):

            parsed = UTILS.parse_resources( fields[1:] )

            defaults = {
                # sets the commodity
                "supply" : False,
                "store" : False,
                "consume" : False,

                "availability" : "",

                # suppliers
                "supplies" : "randint:0,0",

                # consumers
                "consumes" : "randint:0,0",

                # stores
                "initial-capacity" : "randint:0,0",
                "max-capacity" : "",

                "description" : ""
            }

            if parsed.get("consume", False):

                r = MODELS.CommodityConsumer()

                r.initialize(
                    parsed.get("consumes", defaults["consumes"]),
                    commodity=parsed.get("consume"),
                    description=parsed.get("description", defaults["description"]),
                )

                r.availability = parsed.get("availability", defaults["availability"])

                r.save(force_insert=True)
                LOGGER.log( thisApp.DETAIL, "%d.%03d Created %s consumer %s (%s)", *UTILS.from_soldays( thisApp.solday ), r.commodity, r.name, r.consumer_id )

            if parsed.get("store", False):

                r = MODELS.CommodityResevoir()

                r.initialize(
                    parsed.get("max-capacity", defaults["max-capacity"]),
                    initial_capacity=parsed.get("initial-capacity", defaults["initial-capacity"]),
                    commodity=parsed.get("store"),
                    description=parsed.get("description", defaults["description"]),
                )
                r.availability = parsed.get("availability", defaults["availability"])

                r.save(force_insert=True)
                LOGGER.log( thisApp.DETAIL, "%d.%03d Created %s resevoir %s (%s)", *UTILS.from_soldays( thisApp.solday ), r.commodity, r.name, r.store_id )

                c = MODELS.CommodityResevoirCapacity()

                c.initialize(r.store_id,
                             r.commodity,
                             r.commodity_id,
                             capacity=r.initial_capacity)

                c.solday=thisApp.solday
                c.save(force_insert=True)

                EVENTS.register_callback(
                    runon =  thisApp.solday + 1,
                    priority = 1,
                    periodic = 1,
                    callback_func=per_sol_setup_each_commodity_resevoir_storage,
                    kwargs = {
                        "store_id" : c.store_id,
                        "commodity" : c.commodity,
                        "commodity_id" : c.commodity_id
                    }
                )

            if parsed.get("supply", False):

                r = MODELS.CommoditySupplier()

                r.initialize(
                    parsed.get("supplies", defaults["supplies"]),
                    commodity=parsed.get("supply"),
                    description=parsed.get("description", defaults["description"]),
                )
                r.availability = parsed.get("availability", defaults["availability"])

                r.save(force_insert=True)

                LOGGER.log( thisApp.DETAIL, "%d.%03d Created %s supply %s (%s)", *UTILS.from_soldays( thisApp.solday ), r.commodity, r.name, r.supplier_id )


def per_sol_setup_each_commodity_resevoir_storage(**kwargs):
    """
    This is triggered every sol BUT begins one sol after creation so
    that yestersol is already present

    It just copies from yestersol so that we're ready for tosol's consumption/supply

    By being triggered for each resevoir separately it keeps this simple

    This is run as the first callback of the Sol (priority = 1)

    """

    if "store_id" not in kwargs:
        return

    if "commodity_id" not in kwargs:
        return

    if "commodity" not in kwargs:
        return

    capacity = MODELS.CommodityResevoirCapacity.select(
        MODELS.CommodityResevoirCapacity.capacity
    ).filter(
        ( MODELS.CommodityResevoirCapacity.store_id == kwargs["store_id"] ) &
        ( MODELS.CommodityResevoirCapacity.solday == (thisApp.solday - 1) )
    ).scalar()

    c = MODELS.CommodityResevoirCapacity()

    c.initialize( kwargs['store_id'],
                 kwargs['commodity'],
                 kwargs['commodity_id'],
                 capacity=capacity)

    c.solday = thisApp.solday

    c.save(force_insert=True)


def per_sol_commodity_consumption(**kwargs):

    if kwargs.get("idx",0) != 0:
        return

    try:

        query = MODELS.Commodity.select(
            MODELS.Commodity.simulation_id,
            MODELS.Commodity.commodity_id,
            MODELS.Commodity.commodity,
            MODELS.CommodityConsumer.consumer_id,
            MODELS.CommodityConsumer.name.alias('consumer_name'),
            MODELS.CommodityConsumer.is_online.alias('consumer_online'),
            MODELS.CommodityConsumer.consumes,
            MODELS.CommodityConsumer.is_per_settler,
        ).filter(
            MODELS.Commodity.simulation_id == thisApp.simulation
        ).join(
            MODELS.CommodityConsumer,
            peewee.JOIN.LEFT_OUTER,
            attr='consumer',
            on=(MODELS.CommodityConsumer.commodity_id == MODELS.Commodity.commodity_id)
        ).dicts()

        # This handles the fixed commodity
        for row in query.execute():

            ru = MODELS.CommodityUsage()

            ru.initialize( row['commodity'], row['commodity_id'])

            ru.simulation_id = thisApp.simulation

            ru.solday = thisApp.solday

            ru.is_online = row['consumer_online']

            if row['consumer_id']:
                ru.key_type = 'consumer'
                ru.key_id = row['consumer_id']
                ru.name = row['consumer_name']

                if row['consumer_online']:
                    ru.debit = RANDOM.parse_random_value(row['consumes'])
                else:
                    ru.debit = 0.0

                if row['is_per_settler']:
                    ru.debit = ru.debit * thisApp.current_settler_count

            if ru.key_id:
                # there is a trigger that updates the resevoir capacity
                # from these changes...
                ru.save(force_insert=True)

                LOGGER.log( thisApp.DETAIL, "%d.%03d Updated %s's use of %s", *UTILS.from_soldays( thisApp.solday ), ru.name, ru.commodity)


    except Exception as e:

        LOGGER.exception( "%d.%03d: %s", *UTILS.from_soldays( thisApp.solday ), str(e))


def per_sol_commodity_supply(**kwargs):

    if kwargs.get("idx",0) != 0:
        return

    try:

        query = MODELS.Commodity.select(
            MODELS.Commodity.simulation_id,
            MODELS.Commodity.commodity_id,
            MODELS.Commodity.commodity,
            MODELS.CommoditySupplier.supplier_id,
            MODELS.CommoditySupplier.name.alias('supplier_name'),
            MODELS.CommoditySupplier.is_online.alias('supplier_online'),
            MODELS.CommoditySupplier.supplies,
        ).filter(
            MODELS.Commodity.simulation_id == thisApp.simulation
        ).join(
            MODELS.CommoditySupplier,
            peewee.JOIN.LEFT_OUTER,
            attr='supplier',
            on=(MODELS.CommoditySupplier.commodity_id == MODELS.Commodity.commodity_id)
        ).dicts()

        for row in query.execute():

            ru = MODELS.CommodityUsage()

            ru.initialize( row['commodity'], row['commodity_id'])

            ru.simulation_id = thisApp.simulation

            ru.solday = thisApp.solday

            ru.is_online = row['supplier_online']

            if row['supplier_id']:
                ru.key_type = 'supplier'
                ru.key_id = row['supplier_id']
                ru.name = row['supplier_name']

                if row['supplier_online']:
                    ru.credit = RANDOM.parse_random_value(row['supplies'])
                else:
                    ru.credit = 0.0

            if ru.key_id:
                # there is a trigger that updates the resevoir capacity
                # from these changes...
                ru.save(force_insert=True)

                LOGGER.log( thisApp.DETAIL, "%d.%03d Updated %s's use of %s", *UTILS.from_soldays( thisApp.solday ), ru.name, ru.commodity)



    except Exception as e:

        LOGGER.exception( "%d.%03d: %s", *UTILS.from_soldays( thisApp.solday ), str(e))


def per_sol_update_commodity_resevoir_storage(**kwargs):
    """
    Integrates all the day's resource changes into a single update into
    the storage table

    this is scheduled after all the CommodityUsage data has been updated for the day.

    This just needs to apply the Sol's delta to the current record (already
    setup with Sol's starting value in per_sol_setup_each_commodity_resevoir_storage)
    """

    # Supply and Consumption are global (i.e. not per resevoir) demand, so
    # don't join here or its gets big
    stores = {}

    try:

        query = MODELS.CommodityResevoir(
            MODELS.CommodityResevoir.name,
            MODELS.CommodityResevoir.store_id,
            MODELS.CommodityResevoir.commodity,
            MODELS.CommodityResevoir.commodity_id,
            MODELS.CommodityResevoir.max_capacity,
            MODELS.CommodityResevoir.is_online,
            MODELS.CommodityResevoirCapacity.capacity
        ).filter(
            ( MODELS.CommodityResevoir.simulation_id == thisApp.simulation ) &
            ( MODELS.CommodityResevoirCapacity.solday == thisApp.solday ) &
            ( MODELS.CommodityResevoir.is_online == True )
        ).join(
            MODELS.CommodityResevoirCapacity,
            peewee.JOIN.LEFT_OUTER, attr='capacity',
            on=( MODELS.CommodityResevoir.store_id == MODELS.CommodityResevoirCapacity.store_id )
        ).dicts()

        for row in query.execute():

            if row['commodity_id'] not in stores:
                stores[ row['commodity_id'] ] = []

            stores[ row['commodity_id'] ].append( row )

    # pylint: disable-next=bare-except
    except: # nosec try_except_pass
        pass

    tosol_deltas = {}

    try:
        query = MODELS.CommodityUsage.select(
            MODELS.CommodityUsage.commodity,
            MODELS.CommodityUsage.commodity_id,
            MODELS.CommodityUsage.name,
            MODELS.CommodityUsage.credit,
            MODELS.CommodityUsage.debit,
        ).filter(
            ( MODELS.CommodityUsage.simulation_id == thisApp.simulation ) &
            ( MODELS.CommodityUsage.solday == thisApp.solday )
        ).dicts()

        for row in query.execute():

            if row['commodity_id'] not in tosol_deltas:
                tosol_deltas[ row['commodity_id'] ] = 0.0

            tosol_deltas[ row['commodity_id'] ] -= row['debit']


            tosol_deltas[ row['commodity_id'] ] += row['credit']

    # pylint: disable-next=bare-except
    except: # nosec try_except_pass
        pass


    for commodity,stores in stores.items():

        if commodity not in tosol_deltas or len(stores) == 0:
            continue

        total_capacity_across_all_stores = 0.0

        for store in stores:

            update = MODELS.CommodityResevoirCapacity.get(
                MODELS.CommodityResevoirCapacity.store_id == store['store_id'],
                MODELS.CommodityResevoirCapacity.solday == thisApp.solday
            )


            update.capacity += tosol_deltas[ commodity ] / len(stores)

            update.is_online = store['is_online']

            if update.is_online is True:

                if update.capacity < 0.0:

                    if thisApp.allow_negative_commodities == False:

                        update.capacity = 0.0

            update.save()

            total_capacity_across_all_stores += update.capacity


        if total_capacity_across_all_stores < 0.0:
            EVENTS.register_callback(
                runon =  thisApp.solday + 1,
                periodic = 0,
                priority = 0, # most important
                callback_func=EVENTS.callbacks.resource_starvation,
                kwargs = {
                    "commodity" : commodity
                }
            )

def per_sol_commodity_maintenance(**kwargs):

    suppliers = MODELS.CommoditySupplier.select(
        MODELS.CommoditySupplier.supplier_id,
        MODELS.CommoditySupplier.availability
    ).filter(
        ( MODELS.CommoditySupplier.simulation_id == thisApp.simulation ) &
        ( MODELS.CommoditySupplier.is_online == True )
    )

    for row in suppliers.execute():

        if row.availability and RANDOM.parse_random_value(row.availability) < 1 :

            # if we call the functions directly we don't get an entry in the events table...
            EVENTS.register_callback(
                runon =  thisApp.solday + 1,
                periodic = 0,
                # bring it back online tomorrowsol, but _before_ its re-evelauated
                priority = 24,
                callback_func=EVENTS.callbacks.commodity_goes_offline,
                kwargs = {
                    "id" : row.supplier_id,
                    "table" : MODELS.CommodityType.Supplier
                }
            )

            EVENTS.register_callback(
                runon =  thisApp.solday + 2,
                periodic = 0,
                # bring it back online tomorrowsol, but _before_ its re-evelauated
                priority = 24,
                callback_func=EVENTS.callbacks.commodity_goes_online,
                kwargs = {
                    "id" : row.supplier_id,
                    "table" : MODELS.CommodityType.Supplier
                }
            )

    consumers = MODELS.CommodityConsumer.select(
        MODELS.CommodityConsumer.consumer_id,
        MODELS.CommodityConsumer.availability
    ).filter(
        ( MODELS.CommodityConsumer.simulation_id == thisApp.simulation ) &
        ( MODELS.CommodityConsumer.is_online == True )
    )

    for row in consumers.execute():

        if row.availability and RANDOM.parse_random_value(row.availability) < 0:

            EVENTS.register_callback(
                runon =  thisApp.solday + 1,
                periodic = 0,
                priority = 24,
                callback_func=EVENTS.callbacks.commodity_goes_offline,
                kwargs = {
                    "id" : row.consumer_id,
                    "table" : MODELS.CommodityType.Consumer
                }
            )

            EVENTS.register_callback(
                runon =  thisApp.solday + 2,
                periodic = 0,
                priority = 24,
                callback_func=EVENTS.callbacks.commodity_goes_online,
                kwargs = {
                    "id" : row.consumer_id,
                    "table" : MODELS.CommodityType.Consumer
                }
            )

    stores = MODELS.CommodityResevoir.select(
        MODELS.CommodityResevoir.store_id,
        MODELS.CommodityResevoir.availability
    ).filter(
        ( MODELS.CommodityResevoir.simulation_id == thisApp.simulation ) &
        ( MODELS.CommodityResevoir.is_online == True )
    )

    for row in stores.execute():

        if row.availability and RANDOM.parse_random_value(row.availability) is False :

            # bring it back on-line tomorrow
            EVENTS.register_callback(
                runon =  thisApp.solday + 1,
                periodic = 0,
                priority = 24,
                callback_func=EVENTS.callbacks.commodity_goes_offline,
                kwargs = {
                    "id" : row.store_id,
                    "table" : MODELS.CommodityType.Resevoir
                }
            )

            # bring it back on-line tomorrow
            EVENTS.register_callback(
                runon =  thisApp.solday + 2,
                periodic = 0,
                priority = 24,
                callback_func=EVENTS.callbacks.commodity_goes_online,
                kwargs = {
                    "id" : row.store_id,
                    "table" : MODELS.CommodityType.Resevoir
                }
            )


def commodity_goes_online(**kwargs):

    res = None

    if "id" not in kwargs:
        return

    if "table" not in kwargs:
        return


    if kwargs['table'] == MODELS.CommodityType.Consumer:

        res = MODELS.CommodityConsumer.get(consumer_id=kwargs['id'])

    elif kwargs['table'] == MODELS.CommodityType.Supplier:

        res = MODELS.CommoditySupplier.get(supplier_id=kwargs['id'])

    elif kwargs['table'] == MODELS.CommodityType.Resevoir:

        res = MODELS.CommodityResevoir.get(store_id=kwargs['id'])

    if res:

        res.is_online = True

        res.save()

        LOGGER.log(thisApp.NOTICE,
                   '%d.%03d %s %s %s is on-line',
                   *UTILS.from_soldays( thisApp.solday ),
                   res.commodity.capitalize(),
                   kwargs['table'],
                   res.name)


def commodity_goes_offline(**kwargs):

    res = None

    if "id" not in kwargs:
        return

    if "table" not in kwargs:
        return


    if kwargs['table'] == MODELS.CommodityType.Consumer:

        res = MODELS.CommodityConsumer.get(consumer_id=kwargs['id'])

    elif kwargs['table'] == MODELS.CommodityType.Supplier:

        res = MODELS.CommoditySupplier.get(supplier_id=kwargs['id'])

    elif kwargs['table'] == MODELS.CommodityType.Resevoir:

        res = MODELS.CommodityResevoir.get(store_id=kwargs['id'])

    if res:

        res.is_online = False

        res.save()

        LOGGER.log( thisApp.NOTICE,
                   '%d.%03d %s %s %s is off-line',
                   *UTILS.from_soldays( thisApp.solday ),
                   res.commodity.capitalize(),
                   kwargs['table'],
                   res.name)


def resource_starvation(**kwargs):

    LOGGER.log( logging.INFO,
               '%d.%03d Commodity %s has been completely exhausted.',
               *UTILS.from_soldays( thisApp.solday ),
               kwargs['commodity'])

    # TODO need to trigger some error condition, we've run out of X
    #  - reduce consumption
    #  - increase supply
    #  - everyone (slowly) dies until consumption matches supply
