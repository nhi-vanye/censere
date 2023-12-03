## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

from __future__ import division

import peewee

import censere.events.callbacks as CALLBACKS
import censere.events.store as EVENTS
import censere.models as MODELS
import censere.utils as UTILS
import censere.utils.random as RANDOM
from censere import LOGGER
from censere.config import thisApp


##
# Make a single new family out of two singles
# the caller is responsible for calling this at
# appropriate times...
# This may not create a family if there are no compatible singles
#
# \param args - not normally used, but required for pytest benchmarking
def make(*args ):

    ( year, sol ) = UTILS.from_soldays( thisApp.solday )

    LOGGER.info( f'{year}.{sol:03d} Trying to make a new family' )

    partner = MODELS.Settler.alias()

    query = MODELS.Settler.select(
            MODELS.Settler.settler_id.alias('userid1'),
            MODELS.Settler.first_name.alias('first_name1'),
            MODELS.Settler.family_name.alias('family_name1'),
            MODELS.Settler.sex.alias('sex1'),
            partner.settler_id.alias('userid2'),
            partner.first_name.alias('first_name2'),
            partner.family_name.alias('family_name2'),
            partner.sex.alias('sex2')
        ).join(
            partner, on=( partner.simulation_id == MODELS.Settler.simulation_id ), attr="partner"
        ).where(
                # part of this execution run
                ( MODELS.Settler.simulation_id == thisApp.simulation ) &
                ( partner.simulation_id == thisApp.simulation ) &
                # no self-partnering
                ( MODELS.Settler.settler_id != partner.settler_id ) &
                # still alive
                ( MODELS.Settler.death_solday == 0 ) &
                ( partner.death_solday == 0 ) &
                # - both persons must be single - so currently no extended families
                # TODO - this should probably be pushed into the app_family_policy() code
                ( MODELS.Settler.state == 'single' ) &
                ( partner.state == 'single' ) &
                #
                # keep partners close in age as an optimization
                ( peewee.fn.ABS( MODELS.Settler.birth_solday - partner.birth_solday ) < UTILS.years_to_sols(thisApp.partner_max_age_difference) ) &
                #
                # compatible sexuality
                ( MODELS.Settler.orientation.contains( partner.sex ) ) &
                ( partner.orientation.contains( MODELS.Settler.sex ) ) &
                # both over 18 earth years years
                ( MODELS.Settler.birth_solday < (thisApp.solday - UTILS.years_to_sols(18) ) ) &
                ( partner.birth_solday < (thisApp.solday - UTILS.years_to_sols(18) ) ) &
                # Call out to application policy to decide if this is allowed
                # Now implemented a LRU cache as this can get expensive
                # when its called for the same people every day
                ( peewee.fn.app_family_policy( thisApp.common_ancestor, MODELS.Settler.settler_id, partner.settler_id ) == True)
            ).order_by(
# a UUID is close to random and doesn't need to be calculated
                MODELS.Settler.settler_id
                # MODELS.Settler.first_name, partner.first_name
            ).limit(1).dicts()


    num_relationships = 0

    for row in query.execute():

        # rely on triggers to update settler state to couple

        r = MODELS.Relationship()

        r.simulation_id = thisApp.simulation

        r.relationship_id= RANDOM.id()
        r.first=row['userid1']
        r.second=row['userid2']
        r.relationship=MODELS.RelationshipEnum.partner
        r.begin_solday=thisApp.solday

        LOGGER.info( f'{year}.{sol:03d} Creating family between {row["first_name1"]} {row["family_name1"]} and {row["first_name2"]} {row["family_name2"]}')

        r.save()

        relationship_length = RANDOM.parse_random_value( thisApp.relationship_length)
        relationship_ends = thisApp.solday + relationship_length

        EVENTS.register_callback(
            runon= relationship_ends,
            callback_func=CALLBACKS.end_relationship,
            kwargs= { "relationship_id" : r.relationship_id, "simulation": thisApp.simulation }
        )

        num_relationships += 1

        # TODO
        # this seems like a reasonable assumption... if the relationship is shorter than
        # the delay before first child then no children. not biologically required
        # but seems reasonable at this level of sophistication
        #if relationship_length < RANDOM.parse_random_value( thisApp.first_child_delay):
        #    return

        #
        # Doing it here allows us to make children event based - registering next steps
        # when a step completes and we don't have to handle "cool off" state as
        # a special case

        # basic pregnancy steps might be:
        #   reduce productivity after Y months
        #   maternity leave after 8 - for X time
        #   reset productivity after Z as ML ends
        #   paternity leave ? what impact for "frontier" settlements ?
        # those should all be configurable - we don't trigger them all here
        # so that we can model early failures (mothers death or miscariages)

        mother=None
        father=None
        if row['sex1'] != row['sex2']:
            if row['sex1'] == "f":
                mother = row['userid1']
                father = row['userid2']
            else:
                mother = row['userid2']
                father = row['userid1']
        else:
            # TODO - this needs to handle surrogate mothers (and fathers)
            pass

        if mother and father:
            m = MODELS.Settler.get( ( MODELS.Settler.settler_id == str(mother) ) & ( MODELS.Settler.simulation_id == thisApp.simulation ) )

            mothers_age = int( (thisApp.solday - m.birth_solday) / 668 )

            # TODO What percentage of relationships have children ?
            if RANDOM.random() < thisApp.fraction_relationships_having_children :
                r = RANDOM.random()

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

                    birth_day = thisApp.solday + RANDOM.parse_random_value( thisApp.first_child_delay)

                    # if the mother is already pregnant (from a previous relationship) then
                    # add an extra delay.
                    if m.pregnant:
                        birth_day += 668

                    (birthyear, birthsol) = UTILS.from_soldays( birth_day )

                    LOGGER.info( f'{year}.{sol:03d} {row["first_name1"]} {row["family_name1"]} and {row["first_name2"]} {row["family_name2"]} ({mother},{father}) are expecting a child on {birthyear}.{birthsol:03d}')

                    m.pregnant = True
                    m.save()

                    # register a function to be called at `when`
                    EVENTS.register_callback(
                        runon= birth_day,
                        callback_func=CALLBACKS.settler_born,
                        kwargs= {
                            "biological_mother" : mother,
                            "biological_father": father,
                            "simulation": thisApp.simulation
                        }
                    )


    LOGGER.info( f'{year}.{sol:03d} ({thisApp.solday}) Made {num_relationships} new families' )

##
# break up a family (while partners are alive)
# clearing up a family where one member dies is handled
# in the database layer (models/triggers.py)
def breakup( ):
    pass
