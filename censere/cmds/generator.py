#! /usr/bin/env python3

## Copyright (c) 2019,2023 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

import base64
import cProfile
import datetime
import logging
import os
import pathlib
import pickle as ENC  # nosec B403
import pstats
import sys
import uuid

import click

import censere
import censere.cmds.helpers as HELPER
import censere.db as DB
import censere.models as MODELS

# Import the database triggers to handle automation inside the DB
# Not called directly, but still needed
import censere.models.triggers as TRIGGERS  # pylint: disable=unused-import
import censere.utils as UTILS
import censere.utils.random as RANDOM
import censere.version as VERSION
from censere import CONSOLE, LOGGER
from censere.config import thisApp

CENSERE_LOG_DIR = "./"

if "CENSERE_LOG_DIR" in os.environ:
    CENSERE_LOG_DIR = os.environ[ "CENSERE_LOG_DIR" ]

# Allow options of this type to be read from environment variables as a list
# with a `;` separating items.
# To override a default (i.e. --resource), use an environment with a single `;`
class StringList(click.ParamType):
    envvar_list_splitter = ';'

def load_parameters_from_file(ctx, param, value ):
    if value:
        import tomllib
        with open( value, "rb") as params:
            data = tomllib.load(params)
            for var,val in data.items():
                if type(val) == "str":
                    val = value.strip()
                os.environ[ var ] = str(val)

def print_hints_and_exit(ctx, param, value):

    if value is True:
        click.echo( """

The Database should be on a local disk - not in Dropbox etc.

Parameter File
==============

The TOML formatted parameter file uses the environment variable names in the following format

CENSERE_GENERATOR_SEED=1234

For variables that support multiple values (i.e. seed-resource) separate each resource with a `;`. If you want to split the value over multiple lines in the paramter file, then use TOML's triple quoted string - but you still need to use `;` to separate the items

If you want to set an empty variable, you may need to use a single `;` rather than empty string.

The parameter file will provide an updated default, passing the corresponding
option directly on the command line will override it.

Order of precidence (lowest first):

* Environment variables
* --parameters file
* CLI arguments


...
Commodities
===========

The following commodities are currently supported:

  - electricity
  - o2
  - water
  - fuel
  - food


RANDOM Values
=============

This can be calculated using built-in tables from the CDC, or a random function

The option is specified as string:arg1,arg2,..argn

Acceptable Values are:

  cdc:
    use CDC tables (no args are needed). This is only valid for Life Expectancy

  triangular:MIN,PEAK,MAX
    use NUMPY's triangular random function with MIN,PEAK and MAX

  normal:MEAN,STDDEV
    use NUMPY's normal random function with MEAN and STDDEV

  binomial:PROB
    use NUMPY's binomial random function with PROB

  randf:MIN,MAX
    use NUMPY's random_sample (floating point) function between MIN and MAX such that MIN <= F <= MAX

  randint:MIN,MAX
    use NUMPY's randint (integer) random function with MIN and MAX such that MIN <= N <= MAX

  randrange:MIN,MAX
    use NUMPY's randint random function with MIN and MAX such that MIN <= N < MAX

  half:BEGIN,STEP
    There is a 50% probability that a value between BEGIN and BEGIN+STEP will be picked, 25% between BEGIN+STEP and BEGIN+(STEP*2), a 12.5% between BEGIN+(STEP*2) and BEGIN+(STEP*3) etc.

Resource Availability
=====================

The availability of a resource or commodity  is normally thoutght
of as a percentage - i.e. 99.999 (aka five-nines).

Using that method a resource with 99.999% availability would be
offline for under 6minutes per (Earth year)

We calculate availabilty on a daily basis and if unavailable we
take the resource off-line for the entire Sol.

See the RESOURCES.md file for more details on resources.


RANDOMNESS
==========

We use predictable randomness so that its possible to "replay" a
simulation and get the same results, NumPy's RandomState is used
rather than other random modules to allow this.

The state is controlled by the 'random-seed' parameter.

The simulation_id uses a diffent approach to ensure that the
simulation_id is always different and we can therefore merge databases
and compare multiple runs.

""")

        ctx.exit()

##
# Main entry point for execution
#
@click.command("generator")
@click.pass_context
#
# general arguments
#
@click.option( '--random-seed',
        metavar="RAND",
        default=-1,
        help="Seed used to initialize random engine (CENSERE_GENERATOR_RANDOM_SEED)")
@click.option( '--continue-simulation',
        default="",
        metavar="ID",
        help="Continue simulation ID to a new limit (CENSERE_GENERATOR_CONTINUE_SIMULATION)")
@click.option( '--notes',
        metavar="TEXT",
        default="",
        help="Add TEXT into notes column in simulations table (CENSERE_GENERATOR_NOTES)")
@click.option( '--database-dir',
        metavar="DIR",
        default="",
        help="Use a unique file in DIR. This takes priority over --database. Unique file is based on the simulation id (CENSERE_GENERATOR_DATABASE_DIR)")
@click.option( '--parameters',
        metavar="FILE",
        type=click.Path(exists=True),
        callback=load_parameters_from_file,
        is_eager=True,
        help="Read simulation parameters from FILE")
# simulation parameters
#
@click.option( '--astronaut-age-range',
        metavar="RANDOM",
        default="randrange:32,46",
        help="Age range (years) of arriving astronauts (CENSERE_GENERATOR_ASTRONAUT_AGE_RANGE)")
@click.option( '--astronaut-gender-ratio',
        metavar="MALE,FEMALE",
        default="50,50",
        help="Male:Female ratio for astronauts, MUST add up to 100 (CENSERE_GENERATOR_ASTRONAUT_GENDER_RATIO)")
@click.option( '--astronaut-life-expectancy',
        metavar="RANDOM",
        default="cdc:",
        help="Life expectancy of arriving astronauts (CENSERE_GENERATOR_ASTRONAUT_LIFE_EXPECTANCY)")
@click.option( '--common-ancestor',
        metavar="GENERATION",
        type=int,
        default=5,
        help="Allow realtionships where common ancestor is older than GEN. GEN=1 => parent, GEN=2 => grandparent etc (CENSERE_GENERATOR_COMMON_ANCESTOR)")
@click.option( '--first-child-delay',
        metavar="RANDOM",
        default="randint:350,700",
        help="'Delay (sols) between relationship start and first child (CENSERE_GENERATOR_FIRST_CHILD_DELAY)")
@click.option( '--fraction-singles-pairing-per-day',
        metavar="FRACTION",
        type=float,
        default=0.01,
        help="The fraction of singles that will start a relationship PER DAY (CENSERE_GENERATOR_FRACTION_SINGLES_PAIRING)")
@click.option( '--fraction-relationships-having-children',
        metavar="FRACTION",
        type=float,
        default=0.25,
        help="The fraction of relationships that will have children (CENSERE_GENERATOR_FRACTION_RELATIONSHIPS_HAVING_CHILDREN)")
@click.option( '--martian-gender-ratio',
        metavar="MALE,FEMALE",
        default="50,50",
        help="Male:Female ratio for new born martians, MUST add up to 100 (CENSERE_GENERATIOR_MARTIAN_GENDER_RATIO)")
@click.option( '--martian-life-expectancy',
        metavar="RANDOM",
        default="cdc:",
        help="Life expectancy of new born martians (CENSERE_GENERATOR_MARTIAN_LIFE_EXPECTANCY)")
@click.option( '--orientation',
        metavar="HETROSEXUAL,HOMOSEXUAL,BISEXUAL",
        default="90,6,4",
        help="Sexual orientation percentages, MUST add up to 100 (CENSERE_GENERATOR_OREINTATION)")
@click.option( '--partner-max-age-difference',
        metavar="YEARS",
        type=int,
        default=20,
        help="Limit possible relationships to partners with maximum age difference (CENSERE_GENERATOR_PARTNER_MAX_AGE_DIFFERENCE)")
@click.option( '--relationship-length',
  # unverrified reports indicate average marriage lasts 2years 9months
  # this is all relationships, so expect more early breakups, but lets go
  # with 2y9m (earth) as average (1031sols). 30752sols is 82 earth years (100-18)
  # opinion: relationships under 28 days probably aren't exclusive
        metavar="RANDOM",
        default='triangle:28,1031,30752',
        help="How many Sols a relationship lasts (CENSERE_GENERATOR_RELATIONSHIP_LENGTH)")
@click.option( '--sols-between-siblings',
    # TODO confirm this value - based on my extended family
        metavar="RANDOM",
        default="triangle:300,700,1200",
        help="Number of _Sols_ between sibling births (CENSERE_GENERATOR_SOLS_BETWEEN_SIBLINGS)")
@click.option( '--use-ivf/--no-ivf',
        default=False,
        help="Whether to use IFV to extend fertility age range (CENSERE_GENERATOR_USE_IFV)")
#
# Resources
#
@click.option( '--seed-resource',
        metavar="count=RANDOM [supply|store|consume]=ENUM availability=RANDOM [supplies=RANDOM] [consumes=RANDOM] [initial-capacity=RANDOM] [max-capacity=RANDOM]",
        type=StringList(),
        default=[
            # "count=randint:2,4 source=power type=generator avail=randint:99,100 generates=normal:0.4,0.0001 equipment=RTG",
            # TODO:  RTG should have a supply that gradually diminishes over time...
            # 2kW is large for an RTG, but need reliable base supply
            "count=randint:8,16 supply=electricity availability=binomial:0.9999 supplies=normal:2,0.2 description=RTG",
            "count=randint:8,16 store=electricity availability=binomial:0.99 initial-capacity=normal:4.0,0.1 max-capacity=normal:25,1 description=battery",
            "count=randint:1,1 consume=electricity consumes=normal:2,0.2 description=site",
            "count=randint:2,4 store=water availability=binomial:0.9 initial-capacity=normal:1000,100 max-capacity=normal:1500,500 description=tank",
            "count=randint:2,4 store=o2 availability=binomial:0.9 initial-capacity=normal:10000,100 max-capacity=normal:15000,500 description=tank",
        ],
        multiple=True,
        help="Resource supply/demand from seed mission to first settler mission "
              "(CENSERE_GENERATOR_SEED_RESOURCE)")
@click.option( '--resource',
        metavar="count=RANDOM [supply|store|consume]=ENUM availability=RANDOM [supplies=RANDOM] [consumes=RANDOM] [initial-capacity=RANDOM] [max-capacity=RANDOM]",
        default=[
            "count=randint:4,8 store=electricity availability=binomial:0.99 initial-capacity=normal:4.0,0.1 max-capacity=normal:25,1 description=battery",

            "count=randint:4,4 supply=electricity availability=binomial:0.95 supplies=normal:1.5,0.3 description=PV",
            "count=randint:1,1 consume=electricity consumes=normal:4,0.2 description=site",

            "count=randint:4,8 store=water availability=binomial:0.9 initial-capacity=normal:10000,100 max-capacity=normal:12000,500 description=tank",
            "count=randint:2,4 supply=water availability=binomial:0.9 supplies=normal:100,5 description=recycle",
            "count=randint:2,4 supply=o2 availability=binomial:0.9 supplies=normal:5000,500 description=recycle",
        ],
        multiple=True,
        type=StringList(),
        help="Additional commodities arriving on each mission "
              "(CENSERE_GENERATOR_RESOURCE)")
@click.option( '--resource-consumption-per-settler',
        metavar="consume=ENUM consumes=RANDOM",
        type=StringList(),
        default=[
            "consume=electricity consumes=normal:0.5,0.05 description=settlers",
            "consume=water consumes=normal:4.0,0.25 description=drinking",
            "consume=o2 consumes=normal:400,10 description=breathing",
        ],
        multiple=True,
        help="Resource consumption per settler per Sol "
              "(CENSERE_GENERATOR_RESOURCE_CONSUMTION_PER_SETTLER)")
@click.option( '--allow-negative-commodities',
        default=False,
        help="Allow commodity capacity to go negative, helps in tuning commodity supply "
              "(CENSERE_GENERATOR_ALLOW_NEGATIVE_COMMODITIES)")
# mission parameters
#
@click.option( '--seed-resources-lands',
        metavar="SOLS",
        # time for two miniumum transfer orbits + 1 for go/no-go decisions
        # https://www.jpl.nasa.gov/edu/teach/activity/lets-go-to-mars-calculating-launch-windows/
        # 259 Days = 252 Sols
        default= -(3*252),
        type=int,
        help="Number of Sols before initial mission lands that the "
              "resource seed mission lands (CENSERE_GENERATOR_SEED_RESOURCES_LANDS)")
@click.option( '--initial-mission-lands',
        metavar="DATETIME",
        default='2030-01-01 00:00:00.000000+00:00',
        help="Earth date that initial mission lands on Mars (CENSERE_GENERATOR_INITIAL_MISSION_LANDS)")
@click.option( '--limit',
        type=click.Choice(['sols', 'population'], case_sensitive=False),
        default='population',
        help="End simulation when we hit a time or population limit (CENSERE_GENERATOR_LIMIT)")
@click.option( '--limit-count',
        type=int,
        default=1000,
        help="Stop simulation when reaching this sols/population count (CENSERE_GENERATOR_LIMIT_COUNT)")
@click.option( '--mission-lands',
        metavar="RANDOM",
        default="randint:759,759",
        help="Land a new mission every RANDOM sols (CENSERE_GENERATOR_MISSION_LANDS)")
@click.option( '--initial-settlers-per-ship',
        metavar="RANDOM",
        default='randint:20,20',
        help="Number of arriving astronauts (per ship) for the initial mission (CENSERE_GENERATOR_INITIAL_SETTLERS_PER_SHIP)")
@click.option( '--initial-ships-per-mission',
        metavar="RANDOM",
        default='randint:1,1',
        help="Number of ships for the initial mission (CENSERE_GENERATOR_INITIAL_SHIPS_PER_MISSION)")
@click.option( '--settlers-per-ship',
        metavar="RANDOM",
        default='randint:40,40',
        help="Number of arriving astronauts (per ship) for subsequent missions (CENSERE_GENERATOR_SETTLERS_PER_SHIP)")
@click.option( '--ships-per-mission',
        metavar="RANDOM",
        default='randint:1,1',
        help="Number of ships for subsequent missions (CENSERE_GENERATOR_SHIPS_PER_MISSION)")
#
# debug options
#
@click.option( '--cache-details',
        is_flag=True,
        default=False,
        help="Log cache effectiveness as the simulation runs (CENSERE_GENERATOR_CACHE_DETAILS)")
@click.option( '--hints',
        is_flag=True,
        default=False,
        callback=print_hints_and_exit,
        expose_value=False,
        help="Print additional help",
        is_eager=True)
@click.option( '--profile',
        metavar="FILE",
        default="",
        type=click.Path(),
        help="Enable Profiling and safe to FILE")
@click.option( '--use-memory-database/--no-memory-database',
        default=True,
        help="Use SQLite :memory: as main database, and flush to disk every 28 Sols. While faster this can impact memory footprint in limited resource environments")
def cli( ctx,
        random_seed,
        continue_simulation,
        notes,
        database_dir,
        parameters,

        astronaut_age_range,
        astronaut_gender_ratio,
        astronaut_life_expectancy,
        common_ancestor,
        first_child_delay,
        fraction_singles_pairing_per_day,
        fraction_relationships_having_children,
        martian_gender_ratio,
        martian_life_expectancy,
        orientation,
        partner_max_age_difference,
        relationship_length,
        sols_between_siblings,
        use_ivf,

        seed_resource,
        resource,
        resource_consumption_per_settler,
        allow_negative_commodities,

        seed_resources_lands,
        initial_mission_lands,
        limit,
        limit_count,
        mission_lands,
        initial_settlers_per_ship,
        initial_ships_per_mission,
        settlers_per_ship,
        ships_per_mission,

        cache_details,
        # hints is hidden
        profile,
        use_memory_database
       ):
    """Generate simulation data"""

    # dispite its name thisApp is a class and these are class variables
    thisApp.random_seed = random_seed
    thisApp.continue_simulation = continue_simulation
    thisApp.notes = notes
    thisApp.database_dir = database_dir
    thisApp.astronaut_age_range = astronaut_age_range
    thisApp.astronaut_gender_ratio = astronaut_gender_ratio
    thisApp.astronaut_life_expectancy = astronaut_life_expectancy
    thisApp.common_ancestor = common_ancestor
    thisApp.first_child_delay = first_child_delay
    thisApp.fraction_singles_pairing_per_day = fraction_singles_pairing_per_day
    thisApp.fraction_relationships_having_children = fraction_relationships_having_children
    thisApp.martian_gender_ratio = martian_gender_ratio
    thisApp.martian_life_expectancy = martian_life_expectancy
    thisApp.orientation = orientation
    thisApp.partner_max_age_difference = partner_max_age_difference
    thisApp.relationship_length = relationship_length
    thisApp.sols_between_siblings = sols_between_siblings
    thisApp.use_ivf = use_ivf
    thisApp.seed_resources_lands = seed_resources_lands
    thisApp.initial_mission_lands = initial_mission_lands
    thisApp.limit = limit
    thisApp.limit_count = limit_count
    thisApp.mission_lands = mission_lands
    thisApp.initial_settlers_per_ship = initial_settlers_per_ship
    thisApp.initial_ships_per_mission = initial_ships_per_mission
    thisApp.settlers_per_ship = settlers_per_ship
    thisApp.ships_per_mission = ships_per_mission
    thisApp.cache_details = cache_details

    thisApp.seed_resource = seed_resource
    thisApp.resource = resource
    thisApp.resource_consumption_per_settler = resource_consumption_per_settler
    thisApp.allow_negative_commodities = allow_negative_commodities

    ## add legacy aliases
    thisApp.settlers_per_initial_ship = thisApp.initial_settlers_per_ship
    thisApp.ships_per_initial_mission = thisApp.initial_ships_per_mission

    thisApp.enable_profiling = profile
    thisApp.use_memory_database = use_memory_database

    thisApp.report_commodity_status = False

    # this is the only thing that needs to be unique
    # the reset of the IDs should be derrived from the seed value.
    if thisApp.continue_simulation == "":
        thisApp.simulation = str(uuid.uuid4())
    else:
        thisApp.simulation = thisApp.continue_simulation


    LOGGER.remove()

    # this log file is re-used so rotate it
    LOGGER.add(
            sink = f'{CENSERE_LOG_DIR}/censere.log',
            format = "{time:HH:mm:ss} | {level: ^7} | {message}",
            level = "SUCCESS",
            rotation="500 MB"
    )

    # this one has more detail and is specific to a simulation
    LOGGER.add(
            sink = f'{CENSERE_LOG_DIR}/{thisApp.simulation}.log',
            format = "{time:HH:mm:ss} | {level: ^7} | {message}",
            level = "DEBUG" if thisApp.debug is True else "INFO",
    )

    if use_memory_database is True and thisApp.database_dir == "":
        LOGGER.critical( "Incompatable settings, use-memory-database must be used in conjunction with --database-dir")
        sys.exit(1)

    if thisApp.enable_profiling:
        thisApp.profilingHandle = cProfile.Profile()


    # add a defult note
    if thisApp.notes == '':
        thisApp.notes = 'rel-frac={} age-range={} life-expec={}'.format(
            thisApp.fraction_relationships_having_children,
            thisApp.astronaut_age_range,
            thisApp.astronaut_life_expectancy)

    logging.getLogger('peewee').setLevel(logging.INFO)

    if thisApp.debug_sql:
        peewee_logger = logging.getLogger('peewee')
        peewee_logger.addHandler(logging.StreamHandler())
        peewee_logger.setLevel(logging.DEBUG)
        sfilter = censere.AddStackFilter(levels={logging.DEBUG})
        peewee_logger.addFilter(sfilter)

    if thisApp.random_seed == -1:

        thisApp.random_seed = datetime.datetime.now().microsecond

    UTILS.random.seed( thisApp.random_seed )

    if thisApp.dump:
        args = thisApp.args(as_list=True)
        for a in args:
            click.echo( f'{a}' )
        sys.exit(0)



    # takes priority over --database
    if thisApp.database_dir != "":

        p = pathlib.Path( thisApp.database_dir ).joinpath( thisApp.simulation + ".db" )

        p.parent.mkdir(parents=True, exist_ok=True)

        # overwrite anything set using --database
        thisApp.database = str(p)

    HELPER.initialize_database()

    if thisApp.continue_simulation == "":

        thisApp.solday = 0
        thisApp.solday = thisApp.seed_resources_lands - 1

        # all calculations are done in sols (integers from day of settler landing)
        # but convert to earth datetime to make elapsed time easier to comprehend
        # for consistancy downstream we need to ensure datetimes have a consistant format
        # i.e. with microsseconds so add a microsecond...
        thisApp.earth_time = datetime.datetime.fromisoformat(thisApp.initial_mission_lands)

        thisApp.seed_mission_earth_time = thisApp.earth_time - ( thisApp.seed_resources_lands - 1) * datetime.timedelta( seconds=88775, microseconds=244147)

        thisApp.earth_time = thisApp.seed_mission_earth_time


        thisApp.current_settler_count = HELPER.get_current_settler_count()

        s = MODELS.Simulation( )

        s.simulation_id = thisApp.simulation
        s.random_seed = thisApp.random_seed
        s.seed_mission_lands = thisApp.seed_resources_lands
        s.seed_mission_earth_time = thisApp.seed_mission_earth_time
        s.initial_mission_lands = datetime.datetime.fromisoformat(thisApp.initial_mission_lands)
        s.begin_datetime = datetime.datetime.now()
        s.limit_type = thisApp.limit
        s.limit_count = thisApp.limit_count
        s.args = thisApp.args(sep='@')

        if len(thisApp.notes) > 0:
            s.notes = thisApp.notes

        s.save()

    else:

        s = MODELS.Simulation.get( MODELS.Simulation.simulation_id == thisApp.simulation )

        thisApp.solday = s.final_soldays

        RANDOM.set_state( ENC.loads(base64.b64decode(s.random_state)) ) # nosec B301

    ( year, sol ) = UTILS.from_soldays( thisApp.solday )

    # record to a log file before screen
    LOGGER.success( f'{year}.{sol:03d} ({thisApp.solday}) Mars Censere {VERSION.__version__}' )

    LOGGER.success(f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Started.')
    LOGGER.success(f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Seed = {thisApp.random_seed}')
    LOGGER.success(f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Targeting {thisApp.limit} = {thisApp.limit_count}')
    LOGGER.success( f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Updating thisApp.database')

    CONSOLE( f'{year}.{sol:03d} ({thisApp.solday}) Mars Censere {VERSION.__version__}', bold=True )

    CONSOLE( f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Started.', bold=True)

    CONSOLE( f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Seed = {thisApp.random_seed}', bold=True)

    CONSOLE( f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Targeting {thisApp.limit} = {thisApp.limit_count}', bold=True)

    CONSOLE( f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Updating thisApp.database', bold=True)


    if thisApp.continue_simulation == "":

        # just initializes a variable to zero
        # in time for calculating resource consumption
        thisApp.current_settler_count = HELPER.get_current_settler_count()

        HELPER.register_resources()

        # Resources are landed before humans, so we need to
        # loop from negative time until initial landing to
        # handle resource buildup...
        thisApp.solday = thisApp.seed_resources_lands - 1

        HELPER.run_seed_mission()

        thisApp.solday = 0

        HELPER.register_initial_landing()

    if thisApp.use_memory_database:
        # pylint: disable-next=not-context-manager
        with DB.backup.backup("main", DB.db.connection(), "main") as sync:
            while not sync.done:
                sync.step(4096)

    # all calculations are done in sols (integers from day of settler landing)
    # but convert to earth datetime to make elapsed time easier to comprehend
    # for consistancy downstream we need to ensure datetimes have a consistant format
    # i.e. with microsseconds so add a microsecond...
    thisApp.earth_time = datetime.datetime.fromisoformat(thisApp.initial_mission_lands)
    thisApp.earth_time = thisApp.earth_time + datetime.timedelta( microseconds=1 )


    d = MODELS.Demographic()

    d.simulation_id = thisApp.simulation
    d.solday = 1
    d.earth_datetime = thisApp.earth_time
    d.avg_annual_birth_rate = 0.0
    d.avg_annual_death_rate = 0.0
    d.avg_relationships = 0.0
    d.num_relationships_started = 0
    d.num_relationships_ended = 0

    d.save()

    # Run the main mission simulation loop
    HELPER.run_mission()

    if thisApp.enable_profiling:
        stats = pstats.Stats(thisApp.profilingHandle).sort_stats('ncalls')
        stats.dump_stats( thisApp.enable_profiling )

    # Write the final summary entry and other simulation details....
    res = HELPER.add_summary_entry()

    HELPER.add_annual_demographics( )

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

    if thisApp.use_memory_database:
        # pylint: disable-next=not-context-manager
        with DB.backup.backup("main", DB.db.connection(), "main") as sync:
            while not sync.done:
                sync.step(4096)

    ( year, sol ) = UTILS.from_soldays( thisApp.solday )
    LOGGER.success( f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Completed.' )

    LOGGER.success( f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Seed = {thisApp.random_seed}')

    LOGGER.success( f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Final {thisApp.limit} %d >= {HELPER.get_limit_count( thisApp.limit )}' )

    LOGGER.success( f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Updated {thisApp.database}')

    CONSOLE( f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Completed.', bold=True )

    CONSOLE( f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Seed = {thisApp.random_seed}', bold=True)

    CONSOLE( f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Final {thisApp.limit} %d >= {HELPER.get_limit_count( thisApp.limit )}', bold=True )

    CONSOLE( f'{year}.{sol:03d} ({thisApp.solday}) Simulation {thisApp.simulation} Updated {thisApp.database}', bold=True)

    if thisApp.cache_details is True:
        LOGGER.success( f'{year}.{sol:%03} ({thisApp.solday}) Family Policy %s', *UTILS.from_soldays( thisApp.solday ), MODELS.functions.family_policy.cache_info() )
