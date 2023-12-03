#! /usr/bin/env python3
#
# Copyright (c) 2023 Richard Offer, All rights reserved.

# CLI driver for the mars-censere application


import os
import pathlib

import click

import censere
from censere import LOGGER
from censere.config import thisApp

TOPDIR = str(pathlib.PosixPath(censere.__file__).parent)

CFG = os.path.join(
        click.get_app_dir("censere", force_posix=True),
        'config.ini')

CENSERE_LOG_DIR = "./"

if "CENSERE_LOG_DIR" in os.environ:
    CENSERE_LOG_DIR = os.environ[ "CENSERE_LOG_DIR" ]


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
    '--debug/--no-debug',
        default=False,
        is_flag=True,
        help="Run in development mode (additional logging)")
@click.option(
    '--enable-logger',
        'logger_name',
        type=click.Choice([
            "censere.cmds.generator",
            "censere.cmds.merge",
        ]),
    metavar="LOGGER",
    help="Enable (internal) logger",
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
        help="Dump the simulation parameters to stdout and exit (CENSERE_DUMP)")
@click.option(
    '--debug-sql/--no-debug-sql',
        default=False,
        is_flag=True,
        help="Enable debug mode for SQL queries (CENSERE_DEBUG_SQL)")
def cli(ctx, verbose, debug, logger_name, database, dump, debug_sql):

    LOGGER.enable("censere.cli")
    LOGGER.enable("censere.cmds.generator")
    LOGGER.enable("censere.cmds.merge")

    for l in logger_name:
        LOGGER.enable(l)

    ctx.ensure_object(thisApp)

    # these are class variables so we can set them globally
    thisApp.debug = debug
    thisApp.verbose = verbose
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


    thisApp.top_dir = str(pathlib.PosixPath(censere.__file__).parent)
