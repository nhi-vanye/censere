#! /usr/bin/env python3

import argparse
import logging
import sys

import pathlib

import sqlite3

from censere.config import Merge as thisApp
from censere.config import MergeOptions as OPTIONS

import censere.db as DB

## Initialize the parsing of any command line arguments
#
def initialize_arguments_parser( argv ):

    parser = argparse.ArgumentParser(
        fromfile_prefix_chars='@',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Merge multiple Mars Censere databases""",
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

    logging.basicConfig(level=log_level, format=log_msg_format, datefmt='%Y-%m-%dT%H:%M:%S')


## Initialize the database
# Creating it if it doesn't exist and then 
# creating the tables
def initialize_database():

    DB.db.init( thisApp.database ) 

    DB.create_tables()


def main( argv ):

    if pathlib.Path( thisApp.database).exists():

        logging.error( 'For safety the target file (--database=%s) must not exist', thisApp.database)
        sys.exit(1)

    initialize_database()

    cnx = sqlite3.connect( thisApp.database )

    for db in thisApp.args:

        cursor = cnx.cursor()

        cursor.execute("ATTACH DATABASE ? as source",( db, ))

        cursor.execute( "BEGIN TRANSACTION")

        cursor.execute( """
INSERT INTO 
    main.demographics(
        simulation_id,
        solday,
        earth_datetime,
        avg_annual_birth_rate,
        avg_annual_death_rate
    ) 
SELECT 
        simulation_id,
        solday,
        earth_datetime,
        avg_annual_birth_rate,
        avg_annual_death_rate
FROM source.demographics""")

        cursor.execute( "COMMIT")
        cursor.execute( "BEGIN TRANSACTION")

        cursor.execute( """
INSERT INTO 
    main.events(
        simulation_id,
        registered,
        "when",
        callback_func,
        idx,
        args
    ) 
SELECT 
        simulation_id,
        registered,
        "when",
        callback_func,
        idx,
        args
FROM source.events""")

        cursor.execute( "COMMIT")
        cursor.execute( "BEGIN TRANSACTION")

        cursor.execute( """
INSERT INTO 
    main.populations(
    simulation_id,
    solday,
    earth_datetime,
    bucket,
    sol_years,
    sex,
    value
    ) 
SELECT 
    simulation_id,
    solday,
    earth_datetime,
    bucket,
    sol_years,
    sex,
    value
FROM source.populations""")

        cursor.execute( "COMMIT")
        cursor.execute( "BEGIN TRANSACTION")

        cursor.execute( """
INSERT INTO 
    main.relationships(
        simulation_id,
        relationship_id,
        first,
        second,
        relationship,
        begin_solday,
        end_solday
    ) 
SELECT 
        simulation_id,
        relationship_id,
        first,
        second,
        relationship,
        begin_solday,
        end_solday
FROM source.relationships""")

        cursor.execute( "COMMIT")
        cursor.execute( "BEGIN TRANSACTION")

        cursor.execute( """
INSERT INTO 
    main.settlers(
        simulation_id,
        settler_id,
        sex,
        first_name,
        family_name,
        biological_father,
        biological_mother,
        orientation,
        state,
        pregnant,
        birth_location,
        current_location,
        birth_solday,
        death_solday,
        cohort,
        productivity
    ) 
SELECT 
        simulation_id,
        settler_id,
        sex,
        first_name,
        family_name,
        biological_father,
        biological_mother,
        orientation,
        state,
        pregnant,
        birth_location,
        current_location,
        birth_solday,
        death_solday,
        cohort,
        productivity
FROM source.settlers""")

        cursor.execute( "COMMIT")
        cursor.execute( "BEGIN TRANSACTION")

        cursor.execute( """
INSERT INTO 
    main.simulations(
        simulation_id,
        initial_mission_lands,
        begin_datetime,
        end_datetime,
        "limit",
        limit_count,
        mission_ends,
        final_soldays,
        final_population,
        args,
        notes,
        random_seed,
        random_state
    ) 
SELECT 
        simulation_id,
        initial_mission_lands,
        begin_datetime,
        end_datetime,
        "limit",
        limit_count,
        mission_ends,
        final_soldays,
        final_population,
        args,
        notes,
        random_seed,
        random_state 
FROM source.simulations""")

        cursor.execute( "COMMIT")
        cursor.execute( "BEGIN TRANSACTION")

        cursor.execute( """
INSERT INTO 
    main.summary(
        simulation_id,
        solday,
        earth_datetime,
        adults,
        children,
        males,
        females,
        hetrosexual,
        homosexual,
        bisexual,
        population,
        singles,
        couples,
        deaths,
        earth_born,
        mars_born
    ) 
SELECT 
        simulation_id,
        solday,
        earth_datetime,
        adults,
        children,
        males,
        females,
        hetrosexual,
        homosexual,
        bisexual,
        population,
        singles,
        couples,
        deaths,
        earth_born,
        mars_born
FROM source.summary""")

        cursor.execute( "COMMIT")

        cursor.execute("DETACH DATABASE source")


if __name__ == '__main__':

    initialize_arguments_parser( sys.argv[1:] )

    main( sys.argv[1:] )

