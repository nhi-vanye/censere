""" @package events
Original Author: Richard Offer
 
This module implements common event callback functions, these are
registered using `events.register_callback()` to be triggered at some point
in the future

"""

from __future__ import division

import logging
import random
import uuid

from censere.config import Generator as thisApp

import censere.models as MODELS

import censere.utils as UTILS

from .store import register_callback as register_callback

## A person dies
#
def colonist_dies(**kwargs):

    id = None

    for k,v in kwargs.items():
        if k == "id":
            id = v

    if id == None:
        logging.error( "colonist_dies event called with no person identifier")
        return

    logging.log( thisApp.NOTICE, "%d.%d Colonist %s dies ", *UTILS.from_soldays( thisApp.solday ), id )

    # Call the instance method to trigger callback handling.
    for c in MODELS.Colonist().select().filter( MODELS.Colonist.colonist_id == id ):

        c.death_solday = thisApp.solday

        c.save()

## A person is born
#
def colonist_born(**kwargs):

    biological_mother = None
    biological_father = None

    for k,v in kwargs.items():
        if k == "biological_mother":
            biological_mother = v
        if k == "biological_father":
            biological_father = v

    if biological_mother == None or biological_father == None:
        logging.error( "colonist_born event called with no biological parents specified")
        return

    father = None
    mother = None

    try:
        father = MODELS.Colonist.get( MODELS.Colonist.colonist_id == str(biological_father) ) 
        mother = MODELS.Colonist.get( MODELS.Colonist.colonist_id == str(biological_mother) ) 

    except Exception as e:

        logging.error( 'Failed to find parents %s or %s', str(biological_father), str(biological_mother) )
        return

    # Mother died while pregnant - no child
    if mother.death_solday:
        logging.error( '%d.%d Mother %s died while pregnant.', *UTILS.from_soldays( thisApp.solday ), str(biological_mother) )
        return

    m = MODELS.Martian()

    m.initialize( thisApp.solday )

    m.biological_father = biological_father
    m.biological_mother = biological_mother

    m.family_name = father.family_name


    saved = m.save()

    # create the parent <-> child relationship
    r1 = MODELS.Relationship()

    r1.relationship_id=str(uuid.uuid4())
    r1.first=m.colonist_id
    r1.second=mother.colonist_id
    r1.relationship=MODELS.RelationshipEnum.parent
    r1.begin_solday=thisApp.solday

    r1.save()

    r2 = MODELS.Relationship()

    r2.relationship_id=str(uuid.uuid4())
    r2.first=m.colonist_id
    r2.second=father.colonist_id
    r2.relationship=MODELS.RelationshipEnum.parent
    r2.begin_solday=thisApp.solday

    r2.save()

    logging.log( thisApp.NOTICE, '%d.%d Martian %s %s (%s) born', *UTILS.from_soldays( thisApp.solday ), m.first_name, m.family_name, m.colonist_id )

    register_callback(
        when=thisApp.solday + random.gauss( UTILS.years_to_sols(60), UTILS.years_to_sols(10) ),
        callback_func=colonist_dies,
        kwargs= { "id" : m.colonist_id, "name":"{} {}".format( m.first_name, m.family_name) }
    )

    # TODO trying to provide some falloff with age - but this is too simple
    # This should take into account mothers age.
    # dramtic falloff in fertility after 35 ???
    mothers_age = int( (thisApp.solday - mother.birth_solday) / 680 )
    if random.randrange(0,99) < ( 20 - mothers_age )  :
        register_callback( 
            # handle the "cool off" period...
            when= thisApp.solday + random.randrange( 330, 1090),
            callback_func=colonist_born,
            kwargs= { "biological_mother" : mother, "biological_father": father }
        )

##
# A new lander arrives with #colonists
# 
# TODO handle children (imagine aged 10-18, younger than that might be real world difficult)
def mission_lands(**kwargs):

    colonists = kwargs['colonists'] 

    logging.log( thisApp.NOTICE, "%d.%d Mission landed with %d colonists", *UTILS.from_soldays( thisApp.solday ), colonists )

    for i in range(colonists):

        a = MODELS.Astronaut()

        a.initialize( thisApp.solday )

        saved = a.save()

        logging.info( '%d.%d Astronaut %s %s (%s) landed', *UTILS.from_soldays( thisApp.solday ), a.first_name, a.family_name, a.colonist_id )

        # TODO make the max age of death configurable
        # TODO model women outliving men
        # TODO gauss is not a good distribution for modelling human lifetimes
        # TODO life is not evenly distributed about a mean - but its better than a random distribution
        # TODO consider https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3356396/
        # TODO or http://lifetable.de
        # TODO 60 and 10 are just made up...
        # don't let death day be before today or they will never die.
        current_age = thisApp.solday - a.birth_solday
        register_callback( 
            #when= thisApp.solday + max( random.randrange( 1, UTILS.years_to_sols(80) ) - a.birth_solday, 1),
            when= max( random.gauss( UTILS.years_to_sols(60), UTILS.years_to_sols(10) ) - current_age, thisApp.solday+1),
            callback_func=colonist_dies,
            kwargs= { "id" : a.colonist_id, "name":"{} {}".format( a.first_name, a.family_name) }
        )

    # schedule the next landing
    # TODO make the mission size configurable
    # Possible need a growth and random factor
    # - expect for people to travel over time...
    #
    # There is a minimum energy launch window every 780 days =~ 759 sols
    # Assume a commercial organization would want to use it
    # to reduce propellent required for a given payload
    register_callback( 
        when =  thisApp.solday + 759,
        callback_func = mission_lands,
        kwargs = { 
            "colonists" : random.randrange(40, 80)
        }
    )

##
# Break a relationship
# 
# 
def end_relationship(**kwargs):

    id = kwargs['relationship_id'] 

    logging.info("%d.%d Relationship %s ended", *UTILS.from_soldays( thisApp.solday ), id )


    rel = MODELS.Relationship.get( MODELS.Relationship.relationship_id == id )

    rel.end_solday = thisApp.solday

    rel.save()
