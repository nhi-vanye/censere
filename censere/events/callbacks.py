""" @package events
Original Author: Richard Offer
 
This module implements common event callback functions, these are
registered using `events.register_callback()` to be triggered at some point
in the future

"""

import logging
import random

from config import Generator as thisApp

import models

from .store import register_callback as register_callback

## Kill a person some time in the future
# @param kwargs - dict that should contain `id` field indicating which person dies
# @param solday - the solday the person dies (global count from initial landing)
# @param solyear, sol - the solyear and sol within the solyear the person dies
#
def person_dies(solday, solyear, sol, **kwargs):

    id = None

    for k,v in kwargs.items():
        if k == "id":
            id = v

    if id == None:
        logging.error( "person_dies event called with no person identifier")
        return

    logging.info("{}.{}     Colonist {} dies ".format( solyear, sol, id, sol,solday ) )

    session = thisApp.Session()

    for user in session.query( models.Colonist ).filter( models.Colonist.id == id):

        user.death_solday = solday

    session.commit()


## A new person is born some time in the future
# @param kwargs - dict that should contain `id` field indicating which person dies
# @param solday - the solday the person dies (global count from initial landing)
# @param solyear, sol - the solyear and sol within the solyear the person dies
#
def person_born(solday, solyear, sol, **kwargs):

    biological_mother = None

    for k,v in kwargs.items():
        if k == "biological_mother":
            biological_mother = v

    if biological_mother == None:
        logging.error( "person_born event called with no biological_mother specified")
        return

    logging.info("{}.{}     Colonist born {}".format( solyear, sol, id, sol,solday ) )

    session = thisApp.Session()

    # TODO - maternity leave
    # How best o handle both biological mother and family parent's leave ?

    m = models.Martian()

    m.initialize( solday )

    # \TODO set productivity=100 when they get to 18years ???

    session.commit()


##
# A new lander arrives with #adults
# 
# TODO handle children (imagine aged 10-18, younger than that might be difficult)
def mission_lands(solday, solyear, sol, **kwargs):

    adults = kwargs['adults'] 

    logging.info("Mission landed with {} adults at {}.{} ({})".format( adults, solyear, sol, solday) )

    session = thisApp.Session()

    for i in range(adults):

        a = models.Astronaut()

        a.initialize( solday )

        # TODO make the max age of death configurable - 80
        register_callback( 
            when=solday + random.randrange( 1, int( (80*365.25*1.02749125) - a.birth_solday)),
            callback_func=person_dies,
            kwargs= { "id" : a.id }
        )

        session.add(a)

    session.commit()

    # schedule the next landing
    # TODO make the mission size configurable
    # Possible need a growth and random factor
    # - expect for people to travel over time...
    #
    # There is a minimum energy launch window every
    # 780 days =~ 759 sols
    register_callback( 
        when = solday + 759,
        callback_func = mission_lands,
        kwargs = { "adults" : random.randrange(40, 80) }
    )

