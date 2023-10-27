#! /usr/bin/env python3

import click

import logging
import sys

import pathlib

import sqlite3

from censere.config import thisApp

import censere.db as DB

LOGGER = logging.getLogger("c.cli.merge")
DEVLOG = logging.getLogger("d.devel")

## Initialize the database
# Creating it if it doesn't exist and then 
# creating the tables
def initialize_database():

    DB.db.init( thisApp.database ) 

    DB.create_tables()


@click.command("merge-db")
@click.pass_context
@click.argument('args',
        nargs=-1,
        type=click.File('rb'),
        metavar="DB")
def cli( ctx, args ):
    """Merge results from separate databases"""

    if pathlib.Path( thisApp.database).exists():

        LOGGER.error( 'For safety the target file (--database=%s) must not exist', thisApp.database)
        sys.exit(1)

    initialize_database()

    cnx = sqlite3.connect( thisApp.database )

    for db in args:

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
        avg_annual_death_rate,
        avg_partnerships,
        num_partnerships_started,
        num_partnerships_ended,
        num_single_settlers,
        num_partnered_settlers
    ) 
SELECT 
        simulation_id,
        solday,
        earth_datetime,
        avg_annual_birth_rate,
        avg_annual_death_rate,
        avg_partnerships,
        num_partnerships_started,
        num_partnerships_ended,
        num_single_settlers,
        num_partnered_settlers
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



