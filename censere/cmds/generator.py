#! /usr/bin/env python3

## Copyright (c) 2019,2023 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

import click

import base64
import datetime
import logging
import pathlib
import sys
import pickle as ENC
import uuid
import pprint

import censere

#from censere.config import GeneratorOptions as OPTIONS

from censere.config import thisApp

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

LOGGER = logging.getLogger("c.cli.generator")
DEVLOG = logging.getLogger("d.devel")

def print_hints_and_exit(ctx, param, value):

    if value is True:
        click.echo( """

The Database should be on a local disk - not in Dropbox etc.

RANDOM Values
=============

This can be calculated using built-in tables from the CDC, or a random function

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

  half:BEGIN,STEP
    There is a 50% probability that a value between BEGIN and BEGIN+STEP will be picked, 25% between BEGIN+STEP and BEGIN+(STEP*2), a 12.5% between BEGIN+(STEP*2) and BEGIN+(STEP*3) etc.

""")

        ctx.exit()

   
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

        LOGGER.error( e )
    
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

        LOGGER.error( e )

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
@click.command("generator")
@click.pass_context
#
# general arguments
#
@click.option( '--random-seed',
        metavar="RAND",
        default=-1,
        help="Seed used to initialize random engine (CENSERE_GENERATOR_SEED)")
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
#
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
        help="How many SOLS a relationship lasts (CENSERE_GENERATOR_RELATIONSHIP_LENGTH)")
@click.option( '--sols-between-siblings',
    # TODO confirm this value - based on my extended family
        metavar="RANDOM",
        default="triangle:300,700,1200",
        help="Gap between sibling births (CENSERE_GENERATOR_SOLS_BETWEEN_SIBLINGS)")
@click.option( '--use-ivf',
        is_flag=True,
        default=False,
        help="Use IFV to extend fertility (CENSERE_GENERATOR_USE_IFV)")
#
# mission parameters
#
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
def cli( ctx,
        random_seed,
        continue_simulation,
        notes,
        database_dir,

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

        initial_mission_lands,
        limit,
        limit_count,
        mission_lands,
        initial_settlers_per_ship,
        initial_ships_per_mission,
        settlers_per_ship,
        ships_per_mission,

        cache_details
        # hints is hidden
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
    thisApp.initial_mission_lands = initial_mission_lands
    thisApp.limit = limit
    thisApp.limit_count = limit_count
    thisApp.mission_lands = mission_lands
    thisApp.initial_settlers_per_ship = initial_settlers_per_ship
    thisApp.initial_ships_per_mission = initial_ships_per_mission
    thisApp.settlers_per_ship = settlers_per_ship
    thisApp.ships_per_mission = ships_per_mission
    thisApp.cache_details = cache_details

    ## add legacy aliases
    thisApp.settlers_per_initial_ship = thisApp.initial_settlers_per_ship
    thisApp.ships_per_initial_mission = thisApp.initial_ships_per_mission

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

        p.parent.mkdir(parents=True, exist_ok=True)

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

        if len(thisApp.notes) > 0:
            s.notes = thisApp.notes

        s.save()

    else:

        s = MODELS.Simulation.get( MODELS.Simulation.simulation_id == thisApp.simulation )

        thisApp.solday = s.final_soldays

        RANDOM.set_state( ENC.loads(base64.b64decode(s.random_state)) )

    LOGGER.log( thisApp.NOTICE, 'Mars Censere %s', VERSION.__version__ )
    LOGGER.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Started.', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation  )
    LOGGER.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Seed = %d', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.random_seed )
    LOGGER.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Targeted %s = %d', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.limit, thisApp.limit_count )
    LOGGER.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Updating %s', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.database )

    if thisApp.dump:
        excludes=[ 'args', '__module__', 'NOTICE', 'DETAILS', 'TRACE', '__dict__', '__weakref__', '__doc__', 'solday' ]

        for k in sorted(thisApp.__dict__.keys() ):
            if k not in excludes:
                LOGGER.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s --%s=%s', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, k.replace('_','-'), thisApp.__dict__[k] )

        sys.exit(0)


    if thisApp.continue_simulation == "":
        register_initial_landing()

    # all calculations are done in sols (integers from day of landing)
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
            LOGGER.log( thisApp.NOTICE, '%d.%03d (%d) #Settlers %d', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, get_limit_count("population") )

            if thisApp.cache_details:
                LOGGER.log( logging.INFO, '%d.%d Family Policy %s', *UTILS.from_soldays( thisApp.solday ), MODELS.functions.family_policy.cache_info() )

            # returned data not used
            res = add_summary_entry( )
            
        if solyear > 1 and ( sol % 668 ) == 0:

            add_annual_demographics( )

        thisApp.solday += 1
        # from wikipedia
        # https://en.wikipedia.org/wiki/Timekeeping_on_Mars#Sols
        thisApp.earth_time = thisApp.earth_time + datetime.timedelta( seconds=88775, microseconds=244147) 

    res = add_summary_entry()

    add_annual_demographics( )

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

    LOGGER.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Completed.', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation  )
    LOGGER.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Seed = %d', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.random_seed )
    LOGGER.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Final %s %d >= %d', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.limit, get_limit_count( thisApp.limit ), thisApp.limit_count )
    LOGGER.log( thisApp.NOTICE, '%d.%03d (%d) Simulation %s Updated %s', *UTILS.from_soldays( thisApp.solday ), thisApp.solday, thisApp.simulation, thisApp.database )
    LOGGER.log( logging.INFO, '%d.%d Family Policy %s', *UTILS.from_soldays( thisApp.solday ), MODELS.functions.family_policy.cache_info() )

