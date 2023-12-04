## @package config
#
## Copyright (c) 2019-2023 Richard Offer. All right reserved.
#
# see LICENSE.md for license details
#
# Application configuration utilities

# Application configuration
class thisApp(object):

    # common
    verbose = False
    debug = False
    enable_logger = None
    database = None
    dump = False
    debug_sql = False

    # generator
    random_seed = None
    continue_simulation = None
    notes = None
    database_dir = None
    parameters = None
    astronaut_age_range = None
    astronaut_gender_ratio = None
    astronaut_life_expectancy = None
    common_ancestor = None
    first_child_delay = None
    fraction_singles_pairing_per_day = None
    fraction_relationships_having_children = None
    martian_gender_ratio = None
    martian_life_expectancy = None
    orientation = None
    partner_max_age_difference = None
    relationship_length = None
    sols_between_siblings = None
    use_ivf = None
    resources_per_inital_supply_ship = None
    resources_per_supply_ship = None
    resources_per_human_ship = None
    _resource_consumption_per_human = None
    allow_negative_resources = None
    martian_era_earthdate = None
    first_human_mission_lands = None
    supply_mission_period = None
    human_mission_period = None
    return_mission_period = None
    ships_per_initial_supply_mission = None
    ships_per_supply_mission = None
    ships_per_initial_human_mission = None
    ships_per_human_mission = None
    ships_per_return_mission = None
    humans_per_initial_ship = None
    humans_per_ship = None
    humans_per_return_ship = None
    limit = None
    limit_count = None
    cache_details = None
    hints = None
    profile = None
    use_memory_database = None

    # runtime
    simulation = ""

    # cache the IDs for the basic resource to avoid lookups
    # as they don't change within a simulation
    commodity_ids = {}

    colors = {
        "base03" : (0,43,54),
        "base02" : (7,54,66),
        "base01" : (88,110,117),
        "base00" : (101, 123, 131),
        "base0" : (131, 148, 150),
        "base1" : (147,161,161),
        "base2" : (238,232,213),
        "base3" : (253,247,227),
        "yellow" : (181,137,0),
        "orange" : (203,75,22),
        "red" : (220,50,47),
        "magenta" : (211,54,130),
        "violet" : (108,113,196),
        "blue" : (38,39,210),
        "cyan" : (42,161,52),
        "green" : (133,153,0),
    }

    profilingHandle = None

    # used to build a printable string of the "useful" class members
    #
    @classmethod
    def args(cls, sep=" ", as_list=False):

        excludes=[ 'args',
                  '__module__',
                  '__dict__',
                  '__weakref__',
                  '__doc__',
                  '__str__',
                  'NOTICE',
                  'DETAIL',
                  'TRACE',
                  'profilingHandle'
                  'use_memory_database',
                  'cache_details',
                  'enable_profiling',
                  'commodity_ids',
                  'solday',
                  'database',
                  'debug',
                  'debug_sql',
                  'dump',
                  'log_level',
                  'database_dir',
                  'profilingHandle',
                  'random_seed',
                  'top_dir',
                  'use_memory_database',
                  'verbose',
                  'colors'
                 ]

        res=[]


        for v in thisApp.__dict__.keys():

            if v not in excludes:

                res.append( f"{v}={thisApp.__dict__[v]}" )

        res.sort()

        if as_list is True:
            return res

        return sep.join(res)

    @classmethod
    def __str__(cls):
        return cls.args()

def current_simulation():
    """wraps the variable thisApp.solday so that peewee can use it dynamically
    """

    return thisApp.simulation

def current_solday():
    """wraps the variable thisApp.solday so that peewee can use it dynamically
    """

    return thisApp.solday

##
# Dummy class to hold configuration details for the generator
class Viewer:
    NOTICE = 25     # status messages
    DETAILS = 15    # info + additional details
    TRACE = 1


class Merge:
    NOTICE = 25     # status messages
    DETAILS = 15    # info + additional details
    TRACE = 1


## Viewer-specific arguments
#
class ViewerOptions():

    def register(self, parser):

        super().register(parser)

        parser.add_argument( '--save-plots', action="store_true",
            **check_env_for_default( 'CENSERE_SAVE_PLOTS', False ),
            help='Save the plot descriptions into local files for use by orca (CENSERE_SAVE_PLOTS)' )

## Merge-specific arguments
#
class MergeOptions():

    def register(self, parser):

        super().register(parser)

        parser.add_argument( 'args', nargs="+",
            help='List of databases to combine into DATABASE' )
