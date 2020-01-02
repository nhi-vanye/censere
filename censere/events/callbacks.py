## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

""" @package events
 
This module implements common event callback functions, these are
registered using `events.register_callback()` to be triggered at some point
in the future

"""

from __future__ import division

import logging
import uuid

from censere.config import Generator as thisApp

import censere.models as MODELS

import censere.utils as UTILS
import censere.utils.random as RANDOM

import censere.events as EVENTS

from .store import register_callback as register_callback

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
        logging.error( "settler_dies event called with no person identifier")
        return

    logging.log( thisApp.NOTICE, "%d.%03d Settler %s (%s) dies ", *UTILS.from_soldays( thisApp.solday ), name, id )

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
        logging.error( "settler_born event called with no biological parents specified")
        return

    father = None
    mother = None

    try:
        father = MODELS.Settler.get( MODELS.Settler.settler_id == str(biological_father) ) 
        mother = MODELS.Settler.get( MODELS.Settler.settler_id == str(biological_mother) ) 

    except Exception as e:

        logging.error( '%d.%03d Failed to find parents %s (%s) or %s (%s)', *UTILS.from_soldays( thisApp.solday ), father, str(biological_father), mother, str(biological_mother) )
        return

    # Mother died while pregnant - no child
    if mother.death_solday:
        logging.error( '%d.%03d Mother %s died while pregnant.', *UTILS.from_soldays( thisApp.solday ), str(biological_mother) )
        return

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

    logging.log( thisApp.NOTICE, '%d.%03d Martian %s %s (%s) born', *UTILS.from_soldays( thisApp.solday ), m.first_name, m.family_name, m.settler_id )

    age_at_death = RANDOM.parse_random_value( thisApp.martian_life_expectancy, default_value=1, key_in_earth_years=True)


    register_callback(
        when=thisApp.solday + age_at_death,
        callback_func=EVENTS.settler_dies,
        kwargs= { "simulation": thisApp.simulation, "id" : m.settler_id, "name":"{} {}".format( m.first_name, m.family_name) }
    )

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

        logging.log( thisApp.NOTICE, '%d.%03d Sibling of %s %s (%s) to be born on %d.%03d',
            *UTILS.from_soldays( thisApp.solday ),
            m.first_name, m.family_name, m.settler_id, *UTILS.from_soldays( when )  )

        register_callback( 
            # handle the "cool off" period...
            when=when,
            callback_func=EVENTS.settler_born,
            kwargs= {
                "simulation": thisApp.simulation,
                "biological_mother" : mother.settler_id,
                "biological_father": father.settler_id 
            }
        )

##
# A new lander arrives with #settlers
# 
# TODO handle children (imagine aged 10-18, younger than that might be real world difficult)
def mission_lands(**kwargs):

    settlers = kwargs['settlers'] 
    # idx is the index of the function for this day to distinguish
    # between multiple missions landing on the same day
    idx = 0
    if "idx" in kwargs:
        idx = kwargs['idx'] 

    logging.log( thisApp.NOTICE, "%d.%03d Mission landed with %d settlers", *UTILS.from_soldays( thisApp.solday ), settlers )

    for i in range(settlers):

        a = MODELS.Astronaut()

        a.initialize( thisApp.solday )

        saved = a.save()

        logging.info( '%d.%03d Astronaut %s %s (%s) landed', *UTILS.from_soldays( thisApp.solday ), a.first_name, a.family_name, a.settler_id )

        # TODO model women outliving men
        # extra fudge `random.randrange(1, 200)` is to avoid the optics of a number of astronauts dying on the day they land
        # don't let death day be before today or they will never die.
        current_age = thisApp.solday - a.birth_solday

        age_at_death = RANDOM.parse_random_value( thisApp.astronaut_life_expectancy, key_in_earth_years=True)

        date_of_death = a.birth_solday + age_at_death

        register_callback( 
            when= max( date_of_death, thisApp.solday + RANDOM.randrange(1, 200)),
            callback_func=EVENTS.settler_dies,
            kwargs= { "simulation": thisApp.simulation, "id" : a.settler_id, "name":"{} {}".format( a.first_name, a.family_name) }
        )

    # schedule the next landing
    # TODO make the mission size configurable
    # Possible need a growth and random factor
    # - expect for people to travel over time...
    #
    # There is a minimum energy launch window every 780 days =~ 759 sols
    # Assume a commercial organization would want to use it
    # to reduce propellent required for a given payload

    # only register next landing if this is the first landing on this day
    # otherwise we get a cascading landings
    if idx == 0:

        for i in range( RANDOM.parse_random_value( thisApp.ships_per_mission ) ):


            register_callback( 
                when =  thisApp.solday + RANDOM.parse_random_value( thisApp.mission_lands, default_value=759 ),
                callback_func=EVENTS.mission_lands,
                kwargs = { 
                    "simulation": thisApp.simulation,
                    "settlers" : RANDOM.parse_random_value( thisApp.settlers_per_ship )
                }
            )

##
# Break a relationship
# 
# 
def end_relationship(**kwargs):

    id = kwargs['relationship_id'] 

    logging.info("%d.%03d Relationship %s ended", *UTILS.from_soldays( thisApp.solday ), id )


    rel = MODELS.Relationship.get( ( MODELS.Relationship.relationship_id == id ) & ( MODELS.Relationship.simulation_id == thisApp.simulation )  )

    rel.end_solday = thisApp.solday

    rel.save()
