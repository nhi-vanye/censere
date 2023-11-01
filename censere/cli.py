#! /usr/bin/env python3
#
# Copyright (c) 2023 Richard Offer, All rights reserved.

# CLI driver for the mars-censere application

import click

import os
import pathlib

import logging
import logging.config

import censere

from censere.config import thisApp

LOGGER = logging.getLogger("c.cli")
DEVLOG = logging.getLogger("d.devel")

TOPDIR = str(pathlib.PosixPath(censere.__file__).parent)

cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "cmds"))

CONTEXT_SETTINGS = dict(
    auto_envvar_prefix='CENSERE'
)

class CensereCLI(click.Group):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and not filename.startswith("_"):
                rv.append(filename)
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            mod = __import__(f"censere.cmds.{name}", None, None, ["cli"])
        except ImportError:
            return
        return mod.cli

@click.group(cls=CensereCLI, invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option(
    '--verbose',
    '-v',
        default=0,
        type=int,
        help="Set system-wide verbosity")
@click.option(
    '--debug',
        default=False,
        is_flag=True,
        help="Run in development mode (additional logging)")
@click.option(
    '--log-level',
        'log_level',
        metavar="LOGGER=LEVEL",
        help="Override logging level for given logger",
        multiple=True)
@click.option(
    '--database',
        default="censere.db",
        type=click.Path(),
        help="Path to database (CENSERE_DATABASE)")
@click.option(
    '--dump',
        default=False,
        is_flag=True,
        help="Dump the simulation parameters to stdout (CENSERE_DUMP)")
@click.option(
    '--debug-sql',
        default=False,
        is_flag=True,
        help="Enable debug mode for SQL queries (CENSERE_DEBUG_SQL)")
def cli(ctx, verbose, debug, log_level, database, dump, debug_sql):

    ctx.ensure_object(thisApp)

    # these are class variables so we can set them globally
    thisApp.verbose = verbose
    thisApp.log_level = log_level
    thisApp.database = database
    thisApp.dump = dump
    thisApp.debug_sql = debug_sql

    if ctx.invoked_subcommand is None:

        r = CensereCLI()
        click.echo(r.get_help(ctx=ctx))

        click.echo("")
        click.echo("COMMANDS: ")
        cmds = r.list_commands( ctx = ctx) 
        for c in cmds:
            name = c.replace('.py','')
            mod = __import__(f"censere.cmds.{name}", None, None, ["cli"])
            click.echo( f"  {name:>10} - {mod.cli.__doc__}" )

        click.echo("""
For additional help on a command use

    `censere <CMD> --help`
or
    `censere <CMD> --hints`
""")

    logging.addLevelName(thisApp.NOTICE, "NOTICE")
    logging.addLevelName(thisApp.DETAILS, "DETAIL")
    logging.addLevelName(thisApp.TRACE, "TRACE")

    logging.config.dictConfig( censere.LOGGING )

    thisApp.top_dir = str(pathlib.PosixPath(censere.__file__).parent)

    if thisApp.debug is False:
        # disable d.* logging
        logging.getLogger("d.devel").setLevel("ERROR")
        logging.getLogger("d.trace").setLevel("ERROR")

    for kv in log_level:
        s = kv.split("=")
        logging.getLogger( s[0] ).setLevel( s[1] )
        

#if __name__ == '__main__':

#    cli( obj=None , auto_envvar_prefix='CENSERE')

