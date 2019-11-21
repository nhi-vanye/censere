#! /usr/bin/env python3

import argparse
import datetime
import logging
import random
import sys
import uuid

from config import Generator as thisApp
from config import GeneratorOptions as Options

import peewee

import db

import events

import models
# Import the database triggers to handle automation inside the DB
# only needed once 
import models.triggers

import actions

import utils

import version

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

    Options().register( parser )

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

    db.db.init( thisApp.database_url ) 

    db.create_tables()


def initial_landing():

    events.callbacks.mission_lands( colonists=20 )


def get_limit_count( limit="population" ):

    count = 0
    try:
        if limit == "sols":
            count = thisApp.solday

        if limit == "population":

            count = models.Colonist.select().where( 
                ( models.Colonist.simulation == thisApp.simulation ) &
                ( models.Colonist.death_solday == 0 )
            ).count()

    except Exception as e:

        logging.error( e )
    
    return count

def get_singles_count( ):

    count = 0

    try:
        count = models.Colonist.select().where(
            ( models.Colonist.simulation == thisApp.simulation ) &
            ( models.Colonist.death_solday == 0 ) &
            ( models.Colonist.state == 'single' )
        ).count()

    except Exception as e:

        logging.error( e )

    return count

def add_summary_entry():

    adults = models.Colonist.select().where( 
        ( models.Colonist.simulation == thisApp.simulation ) &
        ( models.Colonist.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) ) &
        ( models.Colonist.death_solday == 0 )
    ).count()

    children = models.Colonist.select().where( 
        ( models.Colonist.simulation == thisApp.simulation ) &
        ( models.Colonist.birth_solday >= ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) ) &
        ( models.Colonist.death_solday == 0 )
    ).count()

    singles = models.Colonist.select().where( 
        ( models.Colonist.simulation == thisApp.simulation ) &
        ( models.Colonist.state == 'single' ) & 
        ( models.Colonist.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) ) & 
        ( models.Colonist.death_solday == 0 )
    ).count()

    couples = models.Colonist.select().where( 
        ( models.Colonist.simulation == thisApp.simulation ) &
        ( models.Colonist.state == 'couple' ) & 
        ( models.Colonist.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) ) & 
        ( models.Colonist.death_solday == 0 )
    ).count()

    males = models.Colonist.select().where( 
        ( models.Colonist.simulation == thisApp.simulation ) &
        ( models.Colonist.sex == 'm' ) & 
        ( models.Colonist.death_solday == 0 )
    ).count()

    females = models.Colonist.select().where( 
        ( models.Colonist.simulation == thisApp.simulation ) &
        ( models.Colonist.sex == 'f' ) & 
        ( models.Colonist.death_solday == 0 )
    ).count()

    hetrosexual = models.Colonist.select().where( 
        ( models.Colonist.simulation == thisApp.simulation ) &
        ( ( ( models.Colonist.sex == 'm' ) & 
          ( models.Colonist.orientation == 'f' ) ) | 
        ( ( models.Colonist.sex == 'f' ) & 
          ( models.Colonist.orientation == 'm' ) ) ) &
        ( models.Colonist.death_solday == 0 ) &
        ( models.Colonist.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) )
    ).count()

    homosexual = models.Colonist.select().where( 
        ( models.Colonist.simulation == thisApp.simulation ) &
        ( models.Colonist.sex == models.Colonist.orientation ) & 
        ( models.Colonist.death_solday == 0 ) &
        ( models.Colonist.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) )
    ).count()

    bisexual = models.Colonist.select().where( 
        ( models.Colonist.simulation == thisApp.simulation ) &
        ( models.Colonist.orientation == 'mf' ) & 
        ( models.Colonist.death_solday == 0 ) &
        ( models.Colonist.birth_solday < ( thisApp.solday - int( 18 * 365.25 * 1.02749125 ) ) )
    ).count()

    deaths = models.Colonist.select().where( 
        ( models.Colonist.simulation == thisApp.simulation ) &
        ( models.Colonist.death_solday != 0 )
    ).count()

    earth_born = models.Colonist.select().where( 
        ( models.Colonist.simulation == thisApp.simulation ) &
        ( models.Colonist.birth_location == 'Earth' )
    ).count()

    mars_born = models.Colonist.select().where( 
        ( models.Colonist.simulation == thisApp.simulation ) &
        ( models.Colonist.birth_location == 'Mars' )
    ).count()


    s = models.Summary()

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

    logging.log( thisApp.NOTICE, 'Mars Censere {}'.format( version.__version__ ) )
    logging.log( thisApp.NOTICE, '{}.{} ({}) Simulation {} Started. Goal {} = {}'.format( *utils.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.limit, thisApp.limit_count ) )

    initialize_database()

    # TODO save the paramters into the simulation table for reference.
    s = models.Simulation( )
    s.simulation_id = thisApp.simulation
    s.begin_datetime = datetime.datetime.now()
    s.limit = thisApp.limit
    s.limit_count = thisApp.limit_count
    logging.debug( 'Adding {} rows to simulations table'.format( s.save() ) )

    initial_landing()

    actions.make_families( )

    while get_limit_count( thisApp.limit ) < thisApp.limit_count:

        ( solyear, sol ) = utils.from_soldays( thisApp.solday )

        current_singles_count = get_singles_count()


        # Invoke actions every day...

        # Run any callback scheduled for this solday
        events.invoke_callbacks( )

        # Poulation building
        # TODO make this more flexible
        # Assume: On any given day there is 1% chance of a specific person initiating a relationship
        # there are N singles, so make a family if chance is 0.1 * N or less
        if random.randrange(0,99) < int ( 1 * current_singles_count * 0.5  ):
            actions.make_families( )
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
            logging.log( thisApp.NOTICE, '{}.{} ({}) #Colonists {}'.format( *utils.from_soldays( thisApp.solday ), thisApp.solday, get_limit_count("population") ) )

            add_summary_entry()
            

        thisApp.solday += 1

    add_summary_entry()

    ( 
        models.Simulation.update( { models.Simulation.end_datetime: datetime.datetime.now() } 
            ).where( 
                ( models.Simulation.simulation_id == thisApp.simulation )
            ).execute()
    )

    logging.log( thisApp.NOTICE, '{}.{} ({}) Simulation {} Complete. {} {} >= {}'.format( *utils.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.limit, get_limit_count( thisApp.limit ), thisApp.limit_count ) )

if __name__ == '__main__':

    initialize_arguments_parser( sys.argv[1:] )

    main( sys.argv[1:] )

