#! /usr/bin/env python3

import argparse
import datetime
import logging
import random
import sys
import uuid

import peewee

#make it easy to identify local modules
from censere.config import Generator as thisApp
from censere.config import GeneratorOptions as OPTIONS

import censere.db as DB

import censere.events as EVENTS

import censere.models as MODELS
# Import the database triggers to handle automation inside the DB
# Not called directly, but still needed 
import censere.models.triggers as TRIGGERS

import censere.actions as ACTIONS

import censere.utils as UTILS

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

    log_msg_format = '%(asctime)s %(levelname)5s %(message)s'

    logging.addLevelName(thisApp.NOTICE, "NOTICE")

    log_level = thisApp.NOTICE

    # shortcut
    if thisApp.debug:

        log_msg_format='%(asctime)s.%(msecs)03d %(levelname)5s %(filename)s#%(lineno)-3d %(message)s'

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

    DB.create_tables()


def initial_landing():

    EVENTS.callbacks.mission_lands( colonists=20 )


def get_limit_count( limit="population" ):

    count = 0
    try:
        if limit == "sols":
            count = thisApp.solday

        if limit == "population":

            count = MODELS.Colonist.select().where( 
                ( MODELS.Colonist.simulation == thisApp.simulation ) &
                ( MODELS.Colonist.death_solday == 0 )
            ).count()

    except Exception as e:

        logging.error( e )
    
    return count

def get_singles_count( ):

    count = 0

    try:
        count = MODELS.Colonist.select().where(
            ( MODELS.Colonist.simulation == thisApp.simulation ) &
            ( MODELS.Colonist.death_solday == 0 ) &
            ( MODELS.Colonist.state == 'single' )
        ).count()

    except Exception as e:

        logging.error( e )

    return count

def add_summary_entry():

    adults = MODELS.Colonist.select().where( 
        ( MODELS.Colonist.simulation == thisApp.simulation ) &
        ( MODELS.Colonist.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) ) &
        ( MODELS.Colonist.death_solday == 0 )
    ).count()

    children = MODELS.Colonist.select().where( 
        ( MODELS.Colonist.simulation == thisApp.simulation ) &
        ( MODELS.Colonist.birth_solday >= ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) ) &
        ( MODELS.Colonist.death_solday == 0 )
    ).count()

    singles = MODELS.Colonist.select().where( 
        ( MODELS.Colonist.simulation == thisApp.simulation ) &
        ( MODELS.Colonist.state == 'single' ) & 
        ( MODELS.Colonist.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) ) & 
        ( MODELS.Colonist.death_solday == 0 )
    ).count()

    couples = MODELS.Colonist.select().where( 
        ( MODELS.Colonist.simulation == thisApp.simulation ) &
        ( MODELS.Colonist.state == 'couple' ) & 
        ( MODELS.Colonist.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) ) & 
        ( MODELS.Colonist.death_solday == 0 )
    ).count()

    males = MODELS.Colonist.select().where( 
        ( MODELS.Colonist.simulation == thisApp.simulation ) &
        ( MODELS.Colonist.sex == 'm' ) & 
        ( MODELS.Colonist.death_solday == 0 )
    ).count()

    females = MODELS.Colonist.select().where( 
        ( MODELS.Colonist.simulation == thisApp.simulation ) &
        ( MODELS.Colonist.sex == 'f' ) & 
        ( MODELS.Colonist.death_solday == 0 )
    ).count()

    hetrosexual = MODELS.Colonist.select().where( 
        ( MODELS.Colonist.simulation == thisApp.simulation ) &
        ( ( ( MODELS.Colonist.sex == 'm' ) & 
          ( MODELS.Colonist.orientation == 'f' ) ) | 
        ( ( MODELS.Colonist.sex == 'f' ) & 
          ( MODELS.Colonist.orientation == 'm' ) ) ) &
        ( MODELS.Colonist.death_solday == 0 ) &
        ( MODELS.Colonist.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) )
    ).count()

    homosexual = MODELS.Colonist.select().where( 
        ( MODELS.Colonist.simulation == thisApp.simulation ) &
        ( MODELS.Colonist.sex == MODELS.Colonist.orientation ) & 
        ( MODELS.Colonist.death_solday == 0 ) &
        ( MODELS.Colonist.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) )
    ).count()

    bisexual = MODELS.Colonist.select().where( 
        ( MODELS.Colonist.simulation == thisApp.simulation ) &
        ( MODELS.Colonist.orientation == 'mf' ) & 
        ( MODELS.Colonist.death_solday == 0 ) &
        ( MODELS.Colonist.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) )
    ).count()

    deaths = MODELS.Colonist.select().where( 
        ( MODELS.Colonist.simulation == thisApp.simulation ) &
        ( MODELS.Colonist.death_solday != 0 )
    ).count()

    earth_born = MODELS.Colonist.select().where( 
        ( MODELS.Colonist.simulation == thisApp.simulation ) &
        ( MODELS.Colonist.birth_location == 'Earth' )
    ).count()

    mars_born = MODELS.Colonist.select().where( 
        ( MODELS.Colonist.simulation == thisApp.simulation ) &
        ( MODELS.Colonist.birth_location == 'Mars' )
    ).count()


    s = MODELS.Summary()

    s.simulation_id = thisApp.simulation

    s.solday = thisApp.solday
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



## 
# Main entry point for execution
#
# TODO - turn this funtion into a module
def main( argv ):

    thisApp.simulation = str(uuid.uuid4())

    thisApp.solday = 1

    logging.log( thisApp.NOTICE, 'Mars Censere {}'.format( VERSION.__version__ ) )
    logging.log( thisApp.NOTICE, '{}.{} ({}) Simulation {} Started. Goal {} = {}'.format( *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.limit, thisApp.limit_count ) )

    initialize_database()

    # TODO save the paramters into the simulation table for reference.
    s = MODELS.Simulation( )
    s.simulation_id = thisApp.simulation
    s.begin_datetime = datetime.datetime.now()
    s.limit = thisApp.limit
    s.limit_count = thisApp.limit_count
    logging.debug( 'Adding {} rows to simulations table'.format( s.save() ) )

    initial_landing()

    ACTIONS.make_families( )

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
        if random.randrange(0,99) < int ( 1 * current_singles_count * 0.5  ):
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
            logging.log( thisApp.NOTICE, '{}.{} ({}) #Colonists {}'.format( *UTILS.from_soldays( thisApp.solday ), thisApp.solday, get_limit_count("population") ) )

            add_summary_entry()
            

        thisApp.solday += 1

    add_summary_entry()

    ( 
        MODELS.Simulation.update( { MODELS.Simulation.end_datetime: datetime.datetime.now() } 
            ).where( 
                ( MODELS.Simulation.simulation_id == thisApp.simulation )
            ).execute()
    )

    logging.log( thisApp.NOTICE, '{}.{} ({}) Simulation {} Complete. {} {} >= {}'.format( *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.limit, get_limit_count( thisApp.limit ), thisApp.limit_count ) )

if __name__ == '__main__':

    initialize_arguments_parser( sys.argv[1:] )

    main( sys.argv[1:] )

