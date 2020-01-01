## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

from __future__ import division

import logging
import uuid

import peewee

from censere.config import Generator as thisApp

import censere.models as MODELS

import censere.utils as UTILS
import censere.utils.random as RANDOM

import censere.events.store as EVENTS
import censere.events.callbacks as CALLBACKS

##
# Make a single new family out of two singles
# the caller is responsible for calling this at
# appropriate times...
# This may not create a family if there are no compatible singles
#
# \param args - not normally used, but required for pytest benchmarking
def make(*args ):

    logging.log( logging.INFO, '%d.%d (%d) Trying to make a new family', *UTILS.from_soldays( thisApp.solday ), thisApp.solday )

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
                # compatible sexuality
                ( MODELS.Settler.orientation.contains( partner.sex ) ) &
                ( partner.orientation.contains( MODELS.Settler.sex ) ) &
                # both over 18 earth years years
                ( MODELS.Settler.birth_solday < (thisApp.solday - UTILS.years_to_sols(18) ) ) &
                ( partner.birth_solday < (thisApp.solday - UTILS.years_to_sols(18) ) ) &
                # Call out to application policy to decide if this is allowed
                ( peewee.fn.app_family_policy( MODELS.Settler.settler_id, partner.settler_id ) == True)
            ).order_by(
# a UUID is close to random and doesn't need to be calculated
                MODELS.Settler.settler_id
                # MODELS.Settler.first_name, partner.first_name
            ).limit(1).dicts()

    for row in query.execute():

        # rely on triggers to update settler state to couple

        r = MODELS.Relationship()

        r.simulation_id = thisApp.simulation

        r.relationship_id= RANDOM.id()
        r.first=row['userid1']
        r.second=row['userid2']
        r.relationship=MODELS.RelationshipEnum.partner
        r.begin_solday=thisApp.solday

        logging.log( logging.INFO, '%d.%d Creating family between %s %s and %s %s',
            *UTILS.from_soldays( thisApp.solday ),
            row['first_name1'], row['family_name1'], row['first_name2'], row['family_name2'] )

        r.save()

        # TODO add a callback to randomly break the relationship
        # here (after some random time) or handle it in the main loop ???

        # TODO similar vein - do we handle children here or in main loop ???
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
            if RANDOM.randrange(0,99) < 40:
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

                    delay = [ int(i) for i in thisApp.first_child_delay.split(",") ]

                    birth_day = thisApp.solday + RANDOM.randrange( delay[0], delay[1])

                    logging.log( thisApp.NOTICE, '%d.%03d %s %s and %s %s (%s,%s) are expecting a child on %d.%03d',
                        *UTILS.from_soldays( thisApp.solday ),
                        row['first_name1'], row['family_name1'],
                        row['first_name2'], row['family_name2'],
                        mother, father,
                        *UTILS.from_soldays( birth_day )
                    )

                    # register a function to be called at `when`
                    EVENTS.register_callback(
                        when= birth_day,
                        callback_func=CALLBACKS.settler_born,
                        kwargs= { "biological_mother" : mother, "biological_father": father, "simulation": thisApp.simulation }
                    )

            # TODO this is only breaking up relationships that don't have
            # children - need to make this possible for all relationships
            else:

                EVENTS.register_callback(
                    when= thisApp.solday + RANDOM.randrange( 1, 668),
                    callback_func=CALLBACKS.end_relationship,
                    kwargs= { "relationship_id" : r.relationship_id, "simulation": thisApp.simulation }
                )

##
# break up a family (while partners are alive)
# clearing up a family where one member dies is handled
# in the database layer (models/triggers.py)
def breakup( ):
    pass
