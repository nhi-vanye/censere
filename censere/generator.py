#! /usr/bin/env python3

## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

import argparse
import base64
import datetime
import logging
import pathlib
import sys
import pickle as ENC
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

RANDOM Values
=============

This can be calculated using built-in tables from the CDC, or a random function age

The option is specified as string:arg1,arg2,..argn

Acceptable Values are:

  cdc:
    use CDC tables (no args are needed). This is only valid for Life Expectancy

  triangular:MIN,PEAK,MAX
    use NUMPY's triangular random function with MIN,PEAK and MAX ages (in earth years)

  guass:MEAN,STDDEV
    use NUMPY's guass random function with MEAN and STDDEV ages (in earth years)

  randint:MIN,MAX
    use NUMPY's randint random function with MIN and MAX ages such that MIN <= N <= MAX (in earth years)

  randrange:MIN,MAX
    use NUMPY's randint random function with MIN and MAX ages such that MIN <= N < MAX (in earth years)


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

    for i in range( RANDOM.parse_random_value( thisApp.ships_per_initial_mission, default_value=1 ) ):

        EVENTS.register_callback(
            when =  1,
            callback_func=EVENTS.callbacks.mission_lands,
            kwargs = {
                "settlers" : RANDOM.parse_random_value( thisApp.settlers_per_initial_ship )
            }
        )


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

        logging.error( e )
    
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

        logging.error( e )

    return count

def add_summary_entry():

    s = MODELS.Summary()

    s.initialize()

    s.save()

    return { "solday" : s.solday, "earth_datetime" : s.earth_datetime, "population": s.population }


def add_annual_demographics( ):


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
    if thisApp.continue_simulation == "":
        thisApp.simulation = str(uuid.uuid4())
    else:
        thisApp.simulation = thisApp.continue_simulation

    # takes priority over --database
    if thisApp.database_dir != "":

        p = pathlib.Path( thisApp.database_dir ).joinpath( thisApp.simulation + ".db" )

        # overwrite anything set using --database
        thisApp.database = str(p)

    initialize_database()

    if thisApp.continue_simulation == "":

        thisApp.solday = 0

        s = MODELS.Simulation( )

        s.simulation_id = thisApp.simulation
        s.random_seed = thisApp.random_seed
        s.initial_mission_lands = datetime.datetime.fromisoformat(thisApp.initial_mission_lands)
        s.begin_datetime = datetime.datetime.now()
        s.limit = thisApp.limit
        s.limit_count = thisApp.limit_count
        s.args = thisApp.args(thisApp)
        s.save()

    else:

        s = MODELS.Simulation.get( MODELS.Simulation.simulation_id == thisApp.simulation )

        thisApp.solday = s.final_soldays

        RANDOM.set_state( ENC.loads(base64.b64decode(s.random_state)) )

    logging.log( thisApp.NOTICE, 'Mars Censere %s', VERSION.__version__ )
    logging.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Started.', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation  )
    logging.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Seed = %d', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.random_seed )
    logging.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Targeted %s = %d', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.limit, thisApp.limit_count )
    logging.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Updating %s', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.database )
    logging.log( logging.DEBUG, '%d.%03d (%d) Simulation %s Args %s', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.args(thisApp) )


    if thisApp.continue_simulation == "":
        register_initial_landing()

    # all calculations are done in sols (integers from day of landing)
    # but convert to earth datetime to make elapsed time easier to comprehend
    thisApp.earth_time = datetime.datetime.fromisoformat(thisApp.initial_mission_lands)

    while get_limit_count( thisApp.limit ) < thisApp.limit_count:

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

        # Model resources - both consumed and produced
        # Model inflation


        # give a ~monthly (every 28 sols) and end of year log message
        if ( sol % 28 ) == 0 or sol == 668:
            logging.log( thisApp.NOTICE, '%d.%03d (%d) #Settlers %d', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, get_limit_count("population") )

            # returned data not used
            res = add_summary_entry( )
            
        if solyear > 1 and ( sol % 668 ) == 0:

            add_annual_demographics( )

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
                    MODELS.Simulation.random_state: base64.b64encode(ENC.dumps(RANDOM.get_state())),
                } 
            ).where( 
                ( MODELS.Simulation.simulation_id == thisApp.simulation )
            ).execute()
    )

    logging.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Completed.', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation  )
    logging.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Seed = %d', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.random_seed )
    logging.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Final %s %d >= %d', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.limit, get_limit_count( thisApp.limit ), thisApp.limit_count )
    logging.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Updated %s', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.database )

if __name__ == '__main__':

    initialize_arguments_parser( sys.argv[1:] )

    main( sys.argv[1:] )

