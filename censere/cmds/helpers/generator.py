

import datetime

import censere.actions as ACTIONS
import censere.db as DB
import censere.events as EVENTS
import censere.models as MODELS
import censere.models.functions as FUNC
import censere.utils as UTILS
import censere.utils.random as RANDOM
from censere import CONSOLE, LOGGER
from censere.config import thisApp


## Initialize the database
# Creating it if it doesn't exist and then
# creating the tables
def initialize_database():

    if thisApp.use_memory_database:
        import apsw

        # run the simulation in memory and write to disk on a regular basis
        DB.db.init( ":memory:" ) #thisApp.database )

        DB.backup = apsw.Connection( thisApp.database )

    else:
        DB.db.init( thisApp.database )


    FUNC.register_all( DB.db )

    DB.create_tables()


def register_human_missions():

    for i in range( RANDOM.parse_random_value( thisApp.ships_per_initial_human_mission, default_value=1 ) ):

        EVENTS.register_callback(
            runon =  thisApp.first_human_mission_lands,
            priority = 20,
            periodic=0,
            callback_func=EVENTS.callbacks.human_mission_lands,
            kwargs = {
                "settlers" : thisApp.humans_per_initial_ship
            }
        )

    for i in range( RANDOM.parse_random_value( thisApp.ships_per_human_mission ) ):

        EVENTS.register_callback(
                runon=thisApp.first_human_mission_lands + RANDOM.parse_random_value( thisApp.human_mission_period, default_value=759 ),
                priority=5,
                periodic=RANDOM.parse_random_value( thisApp.human_mission_period, default_value=759 ),
                callback_func=EVENTS.human_mission_lands,
                kwargs = {
                    "simulation": thisApp.simulation,
                    "settlers" : thisApp.humans_per_ship
                }
            )

    EVENTS.register_callback(
            runon =  RANDOM.parse_random_value(thisApp.return_mission_period),
            periodic=RANDOM.parse_random_value( thisApp.return_mission_period, default_value=1498 ),
            priority = 20,
            callback_func=EVENTS.callbacks.return_mission_departs,
            kwargs = {
            }
        )

def register_supply_missions():

    # create the basic resources
    for commodity in [ MODELS.Resource.Other, MODELS.Resource.Electricity, MODELS.Resource.O2, MODELS.Resource.Water, MODELS.Resource.Fuel, MODELS.Resource.Food  ]:

        com = MODELS.Commodity()
        com.initialize( commodity=commodity)
        com.save(force_insert=True)

        # cache the resource id to make it easy to reference the resource without
        # a database lookup
        thisApp.commodity_ids[com.commodity] = com.commodity_id

    # Create the Consumers that represents the per-settler resource consumption
    # pylint: disable-next=not-an-iterable
    if len(thisApp.resource_consumption_per_human):
        thisApp.report_commodity_status = True

    # pylint: disable-next=not-an-iterable
    for res in thisApp.resource_consumption_per_human:

        fields = res.split(" ")

        parsed = UTILS.parse_resources( fields )

        if parsed.get("consume", ""):

            r = MODELS.CommodityConsumer()

            r.initialize(
                parsed.get("consumes", 0.0),
                commodity=parsed.get("consume"),
                description=parsed.get("description", "settlers"),
            )

            r.is_per_settler = True

            # There are no settlers present until Sol `first_human_mission_lands`
            r.is_online = False
            r.save(force_insert=True)

            thisApp.commodity_ids[ f"{parsed.get('consume')}-settler" ] = r.consumer_id

            EVENTS.register_callback(
                runon =  thisApp.first_human_mission_lands,
                priority = 20,
                callback_func=EVENTS.callbacks.commodity_goes_online,
                kwargs = {
                    "table" : MODELS.CommodityType.Consumer,
                    "id" : r.consumer_id
                }
            )

    # Register the callbacks that do the heavy lifting of managing the
    # supply and consumption of resources. Additional callbacks are
    # registered as needed
    EVENTS.register_callback(
            runon =  1,
            priority = 20,
            callback_func=EVENTS.callbacks.supply_mission_lands,
            kwargs = {
                "resources" : thisApp.resources_per_initial_supply_ship
            }
        )

    EVENTS.register_callback(
            runon =  1,
            periodic=RANDOM.parse_random_value( thisApp.supply_mission_period, default_value=759 ),
            priority = 20,
            callback_func=EVENTS.callbacks.supply_mission_lands,
            kwargs = {
                "resources" : thisApp.resources_per_supply_ship
            }
        )

    # human ships also bring resources
    EVENTS.register_callback(
            runon =  thisApp.first_human_mission_lands,
            priority = 20,
            callback_func=EVENTS.callbacks.supply_mission_lands,
            kwargs = {
                "resources" : thisApp.resources_per_human_ship
            }
        )

    EVENTS.register_callback(
            runon =  thisApp.first_human_mission_lands + RANDOM.parse_random_value( thisApp.human_mission_period, default_value=759 ) ,
            periodic=RANDOM.parse_random_value( thisApp.human_mission_period, default_value=759 ),
            priority = 20,
            callback_func=EVENTS.callbacks.supply_mission_lands,
            kwargs = {
                "resources" : thisApp.resources_per_human_ship
            }
        )



    EVENTS.register_callback(
            runon =  1,
            periodic = 1,
            priority = 25,
            callback_func=EVENTS.callbacks.per_sol_commodity_maintenance,
            kwargs = { }
        )

    EVENTS.register_callback(
            runon =  1,
            periodic = 1,
            priority = 40,
            callback_func=EVENTS.callbacks.per_sol_commodity_consumption,
            kwargs = { }
        )

    EVENTS.register_callback(
            runon =  1,
            periodic = 1,
            priority = 50,
            callback_func=EVENTS.callbacks.per_sol_commodity_supply,
            kwargs = { }
        )

    EVENTS.register_callback(
            runon =  1,
            periodic = 1,
            priority = 100,
            callback_func=EVENTS.callbacks.per_sol_update_commodity_resevoir_storage,
            kwargs = { }
        )

def get_current_settler_count():

    count = 0
    try:
        count = MODELS.Settler.select().where(
            ( MODELS.Settler.simulation_id == thisApp.simulation ) &
            ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
            ( MODELS.Settler.death_solday == 0 )
        ).count()

    except Exception as e:

        LOGGER.error( e )

    return count


def get_limit_count( limit="population" ):

    count = 0
    try:
        if limit == "sols":
            count = thisApp.solday

        if limit == "population":

            count = MODELS.Settler.select().where(
                ( MODELS.Settler.simulation_id == thisApp.simulation ) &
                ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
                ( MODELS.Settler.death_solday == 0 )
            ).count()

    except Exception as e:

        CLI.error( e )

    return count

def get_singles_count( ):

    count = 0

    try:
        count = MODELS.Settler.select().where(
            ( MODELS.Settler.simulation_id == thisApp.simulation ) &
            ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
            ( MODELS.Settler.death_solday == 0 ) &
            ( MODELS.Settler.state == 'single' )
        ).count()

    except Exception as e:

        CLI.error( e )

    return count

def get_commodity_storage( solday=None ):

    if solday is None:
        solday = thisApp.solday

    commodities={}

    for commodity in [ MODELS.Resource.Other, MODELS.Resource.Electricity, MODELS.Resource.O2, MODELS.Resource.Water, MODELS.Resource.Fuel, MODELS.Resource.Food  ]:

        try:

            commodities[commodity] = MODELS.CommodityResevoirCapacity.select(
                peewee.fn.Sum(MODELS.CommodityResevoirCapacity.capacity)
            ).where(
                ( MODELS.CommodityResevoirCapacity.simulation_id == thisApp.simulation ) &
                ( MODELS.CommodityResevoirCapacity.solday == solday ) &
                ( MODELS.CommodityResevoirCapacity.commodity == commodity )
            ).scalar()

        except Exception as e:
            CLI.exception(e)

        if commodities[commodity] is None:
            commodities[commodity] = 0.0

    return commodities


def add_summary_entry():

    s = MODELS.Summary()

    s.initialize()

    s.save()

    return { "solday" : s.solday,
            "earth_datetime" : s.earth_datetime,
            "population": s.population,
            "electricity" : s.electricity_stored or float("NaN"),
            "water" : s.water_stored or float("NaN"),
            "o2" : s.o2_stored or float("NaN"),
           }


def add_annual_demographics( ):

    if thisApp.solday < 667:
        return

    # demographics includes birth and death rates
    d = MODELS.Demographic()

    d.initialize()

    d.save()


    # This is population age and gender breakdown
    # useful for population pyramids
    (males, females) = MODELS.get_population_histogram()

    for r in range( len(males[0]) ):

        p = MODELS.Population()

        p.simulation_id = thisApp.simulation

        p.solday = thisApp.solday
        p.earth_datetime = thisApp.earth_time

        p.bucket = "{}-{}".format( males[1][r], males[1][r+1])
        p.sol_years = males[1][r]
        p.sex = 'm'
        p.value = males[0][r]

        p.save()

    for r in range( len( females[0]) ):

        p = MODELS.Population()

        p.simulation_id = thisApp.simulation

        p.solday = thisApp.solday
        p.earth_datetime = thisApp.earth_time
        p.bucket = "{}-{}".format( females[1][r], females[1][r+1])
        p.sol_years = females[1][r]
        p.sex = 'f'
        p.value = females[0][r]

        p.save()


def run_mission():

    if thisApp.enable_profiling:
        thisApp.profilingHandle.enable()

    while get_limit_count( thisApp.limit ) < thisApp.limit_count:

        thisApp.current_settler_count = get_current_settler_count()

        ( solyear, sol ) = UTILS.from_soldays( thisApp.solday )

        current_singles_count = get_singles_count()

        # Invoke actions every day...

        # Run any callback scheduled for this solday
        EVENTS.invoke_callbacks( )

        # Poulation building
        if RANDOM.random() < float(thisApp.fraction_singles_pairing_per_day) * current_singles_count :
            ACTIONS.make_families( )
        # TODO need a model for relationship breakdown
        # break_families()

        # Need a model for multi-person accidents
        #  work or family
        #  occupation
        #  infection/disease
        # consider multi-person accidents, either work or families

        # Model inflation


        # give a ~monthly (every 28 sols) and end of year log message
        if ( sol % 28 ) == 0 or sol == 668:

            ( year, sol ) = UTILS.from_soldays( thisApp.solday )

            LOGGER.log( "INFO", f'{year}.{sol:03d} ({thisApp.solday}) #Settlers {get_limit_count("population")}' )

            if thisApp.cache_details is True:
                LOGGER.log( "INFO", f'{year}.{sol:03d} ({thisApp.solday}) Family Policy {MODELS.functions.family_policy.cache_info()}' )

            res = add_summary_entry( )

            if thisApp.report_commodity_status is True:
                LOGGER.log( "INFO", f'{year}.{sol:03d} ({thisApp.solday}) Stored Resources: Power={res['electricity']:.3f} Water={res['water']:.3f} O2={res['o2']:.3f}' )

            if thisApp.use_memory_database:
                # pylint: disable-next=not-context-manager
                with DB.backup.backup("main", DB.db.connection(), "main") as sync:
                    while not sync.done:
                        sync.step(4096)

        if solyear > 1 and ( sol % 668 ) == 0:


            LOGGER.log( "SUCCESS", f'{year}.{sol:03d} ({thisApp.solday}) #Settlers {get_limit_count("population")}' )
            LOGGER.log( "SUCCESS", f'{year}.{sol:03d} ({thisApp.solday}) Stored Resources: Power={res['electricity']:.3f} Water={res['water']:.3f} O2={res['o2']:.3f}' )

            CONSOLE( f'{year}.{sol:03d} ({thisApp.solday}) New Year Status: #Settlers {get_limit_count("population")}', fg=thisApp.colors["blue"], bold=True )
            CONSOLE( f'{year}.{sol:03d} ({thisApp.solday}) New Year Status: Stored Resources: Power={res['electricity']:.3f} Water={res['water']:.3f} O2={res['o2']:.3f}', fg=thisApp.colors["magenta"], bold=True )

            add_annual_demographics( )

            if thisApp.use_memory_database:
                # pylint: disable-next=not-context-manager
                with DB.backup.backup("main", DB.db.connection(), "main") as sync:
                    while not sync.done:
                        sync.step(4096)

        thisApp.solday += 1
        # from wikipedia
        # https://en.wikipedia.org/wiki/Timekeeping_on_Mars#Sols
        thisApp.earth_time = thisApp.earth_time + datetime.timedelta( seconds=88775, microseconds=244147)

    if thisApp.enable_profiling:
        thisApp.profilingHandle.disable()
