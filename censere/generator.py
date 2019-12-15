#! /usr/bin/env python3

## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

import argparse
import datetime
import logging
import sys
import uuid

#make it easy to identify local modules
from censere.config import Generator as thisApp
from censere.config import GeneratorOptions as OPTIONS

import censere.db as DB

import censere.events as EVENTS

import censere.models as MODELS
# Import the database triggers to handle automation inside the DB
# Not called directly, but still needed 
import censere.models.triggers as TRIGGERS #pylint: disable=unused-import
import censere.models.functions as FUNC


import censere.actions as ACTIONS

import censere.utils as UTILS
import censere.utils.random as RANDOM

import censere.version as VERSION

## Initialize the parsing of any command line arguments
#
def initialize_arguments_parser( argv ):

    parser = argparse.ArgumentParser(
        fromfile_prefix_chars='@',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Mars Censere Generator""",
        epilog="""
Arguments that start with '@' will be considered filenames that
specify arguments to the program - ONE ARGUMENT PER LINE.

The Database should be on a local disk - not in Dropbox etc.
""")

    OPTIONS().register( parser )

    args = parser.parse_args( namespace = thisApp )

    log_msg_format = '%(asctime)s %(levelname)6s %(message)s'

    logging.addLevelName(thisApp.NOTICE, "NOTICE")
    logging.addLevelName(thisApp.DETAILS, "DETAIL")
    logging.addLevelName(thisApp.TRACE, "TRACE")

    log_level = thisApp.NOTICE

    # shortcut
    if thisApp.debug:

        log_msg_format='%(asctime)s.%(msecs)03d %(levelname)6s %(filename)s#%(lineno)-3d %(message)s'

        log_level = logging.DEBUG    

    else:

        log_level = thisApp.log_level

    logging.getLogger('peewee').setLevel(logging.INFO)

    if thisApp.debug_sql:
        peewee_logger = logging.getLogger('peewee')
        peewee_logger.addHandler(logging.StreamHandler())
        peewee_logger.setLevel(logging.DEBUG)

    logging.basicConfig(level=log_level, format=log_msg_format, datefmt='%Y-%m-%dT%H:%M:%S')
    
## Initialize the database
# Creating it if it doesn't exist and then 
# creating the tables
def initialize_database():

    DB.db.init( thisApp.database ) 

    FUNC.register_all( DB.db )

    DB.create_tables()


def register_initial_landing():

    ships_range = [int(i) for i in thisApp.ships_per_initial_mission.split(",") ]

    for i in range(RANDOM.randint( ships_range[0], ships_range[1] ) ):

        settlers_range = [int(i) for i in thisApp.settlers_per_initial_ship.split(",") ]

        EVENTS.register_callback(
            when =  1,
            callback_func=EVENTS.callbacks.mission_lands,
            kwargs = {
                "settlers" : RANDOM.randint(settlers_range[0], settlers_range[1])
            }
        )


def get_limit_count( limit="population" ):

    count = 0
    try:
        if limit == "sols":
            count = thisApp.solday

        if limit == "population":

            count = MODELS.Settler.select().where( 
                ( MODELS.Settler.simulation == thisApp.simulation ) &
                ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
                ( MODELS.Settler.death_solday == 0 )
            ).count()

    except Exception as e:

        logging.error( e )
    
    return count

def get_singles_count( ):

    count = 0

    try:
        count = MODELS.Settler.select().where(
            ( MODELS.Settler.simulation == thisApp.simulation ) &
            ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
            ( MODELS.Settler.death_solday == 0 ) &
            ( MODELS.Settler.state == 'single' )
        ).count()

    except Exception as e:

        logging.error( e )

    return count

def add_summary_entry():

    adults = MODELS.Settler.select().where( 
        ( MODELS.Settler.simulation == thisApp.simulation ) &
        ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
        ( MODELS.Settler.birth_solday < ( thisApp.solday - UTILS.years_to_sols(18) ) ) &
        ( MODELS.Settler.death_solday == 0 )
    ).count()

    children = MODELS.Settler.select().where( 
        ( MODELS.Settler.simulation == thisApp.simulation ) &
        ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
        ( MODELS.Settler.birth_solday >= ( thisApp.solday - UTILS.years_to_sols(18) ) ) &
        ( MODELS.Settler.death_solday == 0 )
    ).count()

    singles = MODELS.Settler.select().where( 
        ( MODELS.Settler.simulation == thisApp.simulation ) &
        ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
        ( MODELS.Settler.state == 'single' ) & 
        ( MODELS.Settler.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) ) & 
        ( MODELS.Settler.death_solday == 0 )
    ).count()

    couples = MODELS.Settler.select().where( 
        ( MODELS.Settler.simulation == thisApp.simulation ) &
        ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
        ( MODELS.Settler.state == 'couple' ) & 
        ( MODELS.Settler.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) ) & 
        ( MODELS.Settler.death_solday == 0 )
    ).count()

    males = MODELS.Settler.select().where( 
        ( MODELS.Settler.simulation == thisApp.simulation ) &
        ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
        ( MODELS.Settler.sex == 'm' ) & 
        ( MODELS.Settler.death_solday == 0 )
    ).count()

    females = MODELS.Settler.select().where( 
        ( MODELS.Settler.simulation == thisApp.simulation ) &
        ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
        ( MODELS.Settler.sex == 'f' ) & 
        ( MODELS.Settler.death_solday == 0 )
    ).count()

    hetrosexual = MODELS.Settler.select().where( 
        ( MODELS.Settler.simulation == thisApp.simulation ) &
        ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
        ( ( ( MODELS.Settler.sex == 'm' ) & 
          ( MODELS.Settler.orientation == 'f' ) ) | 
        ( ( MODELS.Settler.sex == 'f' ) & 
          ( MODELS.Settler.orientation == 'm' ) ) ) &
        ( MODELS.Settler.death_solday == 0 ) &
        ( MODELS.Settler.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) )
    ).count()

    homosexual = MODELS.Settler.select().where( 
        ( MODELS.Settler.simulation == thisApp.simulation ) &
        ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
        ( MODELS.Settler.sex == MODELS.Settler.orientation ) & 
        ( MODELS.Settler.death_solday == 0 ) &
        ( MODELS.Settler.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) )
    ).count()

    bisexual = MODELS.Settler.select().where( 
        ( MODELS.Settler.simulation == thisApp.simulation ) &
        ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
        ( MODELS.Settler.orientation == 'mf' ) & 
        ( MODELS.Settler.death_solday == 0 ) &
        ( MODELS.Settler.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) )
    ).count()

    deaths = MODELS.Settler.select().where( 
        ( MODELS.Settler.simulation == thisApp.simulation ) &
        ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
        ( MODELS.Settler.death_solday != 0 )
    ).count()

    earth_born = MODELS.Settler.select().where( 
        ( MODELS.Settler.simulation == thisApp.simulation ) &
        ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
        ( MODELS.Settler.birth_location == MODELS.LocationEnum.Earth )
    ).count()

    mars_born = MODELS.Settler.select().where( 
        ( MODELS.Settler.simulation == thisApp.simulation ) &
        ( MODELS.Settler.current_location == MODELS.LocationEnum.Mars ) &
        ( MODELS.Settler.birth_location == MODELS.LocationEnum.Mars )
    ).count()


    s = MODELS.Summary()

    s.simulation_id = thisApp.simulation

    s.solday = thisApp.solday
    s.earth_datetime = thisApp.earth_time
    s.adults = adults
    s.children = children

    s.males = males
    s.females = females

    s.hetrosexual = hetrosexual
    s.homosexual = homosexual
    s.bisexual = bisexual

    s.population = adults + children

    s.singles = singles
    s.couples = couples

    s.deaths = deaths

    s.earth_born = earth_born
    s.mars_born = mars_born

    s.save()

    return { "solday" : s.solday, "earth_datetime" : s.earth_datetime, "population": s.population }



## 
# Main entry point for execution
#
# TODO - turn this funtion into a module
def main( argv ):


    if thisApp.random_seed == -1:
    
        thisApp.random_seed = datetime.datetime.now().microsecond

    UTILS.random.seed( thisApp.random_seed )

    # this is the only thing that needs to be unique
    # the reset of the IDs should be derrived from the seed value.
    thisApp.simulation = str(uuid.uuid4())

    thisApp.solday = 0

    logging.log( thisApp.NOTICE, 'Mars Censere %s', VERSION.__version__ )
    logging.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Started. Goal %s = %d, Seed = %d', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.limit, thisApp.limit_count, thisApp.random_seed )

    initialize_database()

    # TODO save the paramters into the simulation table for reference.
    s = MODELS.Simulation( )
    s.simulation_id = thisApp.simulation
    s.initial_mission_lands = datetime.datetime.fromisoformat(thisApp.initial_mission_lands)
    s.begin_datetime = datetime.datetime.now()
    s.limit = thisApp.limit
    s.limit_count = thisApp.limit_count
    s.args = thisApp.args(thisApp)

    register_initial_landing()

    # all calculations are done in sols (integers from day of landing)
    # but convert to earth datetime to make elapsed time easier to comprehend
    thisApp.earth_time = datetime.datetime.fromisoformat(thisApp.initial_mission_lands)

    #ACTIONS.make_families( )

    while get_limit_count( thisApp.limit ) < thisApp.limit_count:

        ( solyear, sol ) = UTILS.from_soldays( thisApp.solday )

        current_singles_count = get_singles_count()

        # Invoke actions every day...

        # Run any callback scheduled for this solday
        EVENTS.invoke_callbacks( )

        # Poulation building
        # TODO make this more flexible
        # Assume: On any given day there is 1% chance of a specific person initiating a relationship
        # there are N singles, so make a family if chance is 0.1 * N or less
        if RANDOM.randrange(0,99) < int ( 1 * current_singles_count * 0.5  ):
            ACTIONS.make_families( )
        # TODO need a model for relationship breakdown
        # break_families()

        # Need a model for multi-person accidents
        #  work or family
        #  occupation
        #  infection/disease
        # consider multi-person accidents, either work or families

        # Model resources - both consumed and produced
        # Model inflation


        # give a ~monthly (every 28 sols) and end of year log message
        if ( sol % 28 ) == 0 or sol == 688:
            logging.log( thisApp.NOTICE, '%d.%03d (%d) #Settlers %d', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, get_limit_count("population") )

            # returned data not used
            res = add_summary_entry()
            

        thisApp.solday += 1
        # from wikipedia
        # https://en.wikipedia.org/wiki/Timekeeping_on_Mars#Sols
        thisApp.earth_time = thisApp.earth_time + datetime.timedelta( seconds=88775, microseconds=244147) 

    res = add_summary_entry()

    ( 
        MODELS.Simulation.update( 
                { 
                    MODELS.Simulation.end_datetime: datetime.datetime.now(),
                    MODELS.Simulation.mission_ends: res["earth_datetime"],
                    MODELS.Simulation.final_soldays: res["solday"],
                    MODELS.Simulation.final_population: res["population"],
                } 
            ).where( 
                ( MODELS.Simulation.simulation_id == thisApp.simulation )
            ).execute()
    )

    logging.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Complete. %s %d >= %d', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.limit, get_limit_count( thisApp.limit ), thisApp.limit_count )

if __name__ == '__main__':

    initialize_arguments_parser( sys.argv[1:] )

    main( sys.argv[1:] )

