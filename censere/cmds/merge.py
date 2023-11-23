#! /usr/bin/env python3

import logging
import pathlib

import click

import censere.db as DB
from censere.config import thisApp

LOGGER = logging.getLogger("c.cli.merge")
DEVLOG = logging.getLogger("d.devel")

@click.command("merge-db")
@click.pass_context
@click.argument('args',
        nargs=-1,
        type=click.Path(exists=True),
        metavar="DB")
def cli( ctx, args ):
    """Merge results from separate databases"""

    if pathlib.Path( thisApp.database ).exists():

        LOGGER.error( 'For safety the target database file (%s) must not exist', thisApp.database)
        #sys.exit(1)


    DB.db.init( thisApp.database )

    DB.create_tables()

    cursor = DB.db.cursor()

    schema = {}

    for t in cursor.execute("PRAGMA table_list"):

        if "sqlite_" in t[1]:
            continue

        if t[1] not in schema:
            schema[ t[1] ] = []

        cursor2 = DB.db.cursor()
        for c in cursor2.execute(f"PRAGMA table_info({t[1]})"):
            if c[1] != "id":
                schema[ t[1] ].append(c[1])

    for src in args:

        LOGGER.log( thisApp.NOTICE, f"Merging results from {src}")

        cursor = DB.db.cursor()

        cursor.execute("ATTACH DATABASE ? as source",( src, ))

        # we can't merge the (internal) 'id' column as it will be non-unique

        for tbl,cols in schema.items():

            LOGGER.log( thisApp.NOTICE, f"  Merging {tbl}")
            cursor.execute( "BEGIN TRANSACTION")

            ins = f"INSERT INTO main.{tbl}({','.join(cols)}) SELECT {','.join(cols)} from source.{tbl}" # nosec: B608

            LOGGER.debug( ins )

            cursor.execute( ins )

            cursor.execute( "COMMIT")

        cursor.execute("DETACH DATABASE source")

        LOGGER.log( thisApp.NOTICE, f"Merged {src}")
