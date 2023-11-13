## @package config
#
## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details
#
# Application configuration utilities

# Application configuration
class thisApp(object):
    NOTICE = 25     # higher value status messages
    # INFO == 20
    DETAIL = 15    # info + additional details
    TRACE = 1

    verbose = None
    debug = False
    log_level = None
    database = ""
    dump = False
    debug_sql = False
    random_seed = None
    continue_simulation = None
    notes = None
    database_dir = ""
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
    seed_resources_lands = None
    initial_mission_lands = None
    limit = None
    limit_count = None
    mission_lands = None
    initial_settlers_per_ship = None
    initial_ships_per_mission = None
    settlers_per_ship = None
    ships_per_mission = None
    cache_details = None
    enable_profiling = None

    seed_resource = None
    seed_resource_consumption_per_sol = None
    resource = None
    resource_consumption_per_settler = None
    resource_consumption_per_sol = None

    # runtime
    simulation = ""

    # cache the IDs for the basic resource to avoid lookups
    # as they don't change within a simulation
    commodity_ids = {}

    # used to build a printable string of the "useful" class members
    # 
    def args(as_list=False):

        # random_seed has its own column
        excludes=[ 'args',
                  '__module__',
                  '__dict__',
                  '__weakref__',
                  '__doc__',
                  '__str__',
                  'NOTICE',
                  'DETAILS',
                  'TRACE',
                  'solday',
                  'database',
                  'debug',
                  'debug_sql',
                  'dump',
                  'log_level',
                 ]

        res=[]


        for v in sorted(thisApp.__dict__.keys()):

            if v not in excludes:

                res.append( f"{v}={thisApp.__dict__[v]}" )

        if as_list is True:
            return res

        return " ".join(res)

    def __str__():
        return args()

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

