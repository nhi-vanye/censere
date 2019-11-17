#! /usr/bin/env python3

import argparse
import datetime
import logging
import random
import sys
import uuid

import sqlalchemy as SA
import sqlalchemy.orm as ORM

from config import Generator as thisApp
from config import GeneratorOptions as Options


import events

import models
# Import the database triggers to handle automation inside the DB
# only needed once 
import models.triggers

import actions
#import db.triggers

# initial landing
global sol
global solday
global solyear
sol = 1
solday=1
solyear=1



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

    log_msg_format = '%(asctime)s.%(msecs)03d %(levelname)5s %(message)s'

    log_level = logging.INFO

    if thisApp.debug:

        log_msg_format='%(asctime)s.%(msecs)03d %(levelname)5s %(filename)s#%(lineno)-3d %(message)s'

        log_level = logging.DEBUG    

    logging.basicConfig(level=log_level, format=log_msg_format, datefmt='%Y-%m-%dT%H:%M:%S')
    
## Initialize the database
# Creating it if it doesn't exist and then 
# creating the tables
def initialize_database():

    # SQLite files should NOT be in a Dropbox directory
    thisApp.engine = SA.create_engine( thisApp.database_url, echo=thisApp.debug_sql)

    thisApp.Session = ORM.sessionmaker( bind=thisApp.engine )

    # create the database schema
    models.Base.metadata.create_all( thisApp.engine )


def initial_landing():
    logging.info( '{}.{}'.format( solyear,sol ) )
    events.callbacks.mission_lands(solday, solyear, sol, adults=10)



def get_limit_count( limit="population" ):

    count = 0
    if limit == "sols":
        count = solday
    if limit == "population":
        count = solday

        session = thisApp.Session()

        count = session.query( models.Colonist.id ).filter_by( simulation = thisApp.simulation).filter_by(death_solday=0).count()

        session.flush()

    return count

def get_singles_count( ):

    count = 0
    session = thisApp.Session()

    count = session.query( models.Colonist.id ).filter_by( simulation = thisApp.simulation).filter_by(death_solday=0).filter_by( state = 'single').count()

    session.flush()

    return count

## 
# Main entry point for execution
#
def main( argv ):

    global sol
    global solyear
    global solday

    thisApp.simulation = str(uuid.uuid4())

    initialize_database()

    session = thisApp.Session()
    s = models.Simulation()

    s.id = thisApp.simulation
    s.begin_datetime = datetime.datetime.now()
    session.commit()

    initial_landing()
    actions.make_families( solday, solyear, sol )
    session = thisApp.Session()

    for c in session.query( models.Colonist ).filter( models.Colonist.state == 'couple').order_by( SA.sql.functions.random() ).limit(1):
        logging.info( c.id )
        c.death_solday = 1

    session.commit()
    
    while get_limit_count( thisApp.limit ) < thisApp.limit_count:

        current_singles_count = get_singles_count()

        # give a monthly (every 28 sols) log message
        if ( sol % 28 ) == 0:
            logging.info( '{}.{} ({}) #Colonists {}'.format( solyear,sol, solday, get_limit_count("population") ) )
            # TODO record summary

        # Invoke actions every day...

        # Run any callback scheduled for this solday
        events.invoke_callbacks( solday, solyear, sol)

        # Poulation building
        # TODO make this more flexible
        # Assume: On any given day there is 1% chance of a specific person initiating a relationship
        # there are N singles, so make a family if chance is 0.1 * N or less
        if random.randrange(0,99) < int ( 1 * current_singles_count * 0.5 ):
            actions.make_families( solday, solyear, sol )
        # TODO need a model for relationship breakdown
        # break_families()

        # Need a model for multi-person accidents
        #  work or family
        #  occupation
        #  infection/disease
        # consider multi-person accidents, either work or families

        # Model resources - both consumed and produced
        # Model inflation

        sol += 1
        solday += 1

        # reset as new year
        if ( solday % 668 ) == 0:

            solyear += 1
            sol = 1
            
    session = thisApp.Session()

    for s in session.query( models.Simulation ).filter( models.Simulation.id == thisApp.simulation):
        s.end_datetime = datetime.datetime.now()
        s.soldays_elapsed = soldays

    session.commit()

    logging.info( '{}.{} ({}) Simulation Complete, {} = {}'.format( solyear,sol, solday, thisApp.limit, thisApp.limit_count ) )


if __name__ == '__main__':

    initialize_arguments_parser( sys.argv[1:] )

    main( sys.argv[1:] )

