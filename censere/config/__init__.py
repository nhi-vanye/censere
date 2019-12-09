## @package config
#
# Original Author: Richard Offer
# Copyright (c) 2019
#
# Application configuration utilities

import os


##
# \brief Check if env variable is set and use its value, else the supplied default value 

# \return dict containing `default` key and its value
#
# @param var_name - environment varaible name to look up
# @param default - value to use as default if `var_name` is not found
#
def check_env_for_default(var_name, default):
    """
If the environment variable VAR_NAME is present
then use its value, otherwise use default
"""

    if os.environ.get(var_name):

        if os.environ.get(var_name).lower() in [ 'true', 'on' ]:
            return { 'default' : True }
        elif os.environ.get(var_name).lower() in [ 'false', 'off', '' ]:
            return { 'default' : False }

        return { 'default' : os.environ.get(var_name) }
    else:
        return { 'default' : default }



##
# Dummy class to hold configuration details for the generator
class Generator:
    NOTICE = 25     # status messages
    DETAILS = 15    # info + additional details
    TRACE = 1

    def args(self):

        excludes=[ 'args', '__module__', 'NOTICE', 'DETAILS', 'TRACE', '__dict__', '__weakref__', '__doc__', 'solday', 'database', 'debug', 'debug_sql', 'log_level', 'simulation' ]

        res=""


        for v in sorted(self.__dict__.keys()):

            if v not in excludes:

                res += "{}={} ".format( v, self.__dict__[v] )

        return res

##
# Dummy class to hold configuration details for the generator
class Viewer:
    NOTICE = 25     # status messages
    DETAILS = 15    # info + additional details
    TRACE = 1



## Arguments that are common to all programs
#
class CommonOptions:

    def register(self, parser):

        parser.add_argument( '--database', action="store",
            metavar="FILE",
            **check_env_for_default( 'CENSERE_DATABASE', 'censere.db' ),
            help='Path to database (CENSERE_DATABASE)' )

        parser.add_argument( '--debug', action="store_true",
            **check_env_for_default( 'CENSERE_DEBUG', False ),
            help='Enable debug mode (CENSERE_DEBUG)' )

        parser.add_argument( '--log-level', action="store",
            type=int,
            **check_env_for_default( 'CENSERE_LOG_LEVEL', 25 ),
            help='Enable debug mode: 15=DETAILS, 20=INFO, 25=NOTICE (CENSERE_LOG_LEVEL)' )

        parser.add_argument( '--debug-sql', action="store_true",
            **check_env_for_default( 'CENSERE_DEBUG_SQL', False ),
            help='Enable debug mode for SQL queries (CENSERE_DEBUG_SQL)' )


## Generator-specific arguments
#
class GeneratorOptions(CommonOptions):

    def register(self, parser):

        super().register(parser)
 
        # Keep these sorted for ease of use

        parser.add_argument( '--astronaut-age-range', action="store",
            metavar="MIN,MAX",
            **check_env_for_default( 'CENSERE_ASTRONAUT_AGE_RANGE', '32,45' ),
            help='Age range (years) of arriving astronauts (CENSERE_ASTRONAUT_AGE_RANGE)' )

        parser.add_argument( '--astronaut-gender-ratio', action="store",
            metavar="MALE,FEMALE",
            **check_env_for_default( 'CENSERE_ASTRONAUT_GENDER_RATIO', '50,50' ),
            help='Male:Female ratio for astronauts, MUST add up to 100 (CENSERE_ASTRONAUT_GENDER_RATIO)' )

        parser.add_argument( '--gap-between-children', action="store",
            metavar="MIN,MAX",
            **check_env_for_default( 'CENSERE_GAP_BETWEEN_CHILDREN', '380,1000' ),
            help='Sols between sibling births (CENSERE_GAP_BETWEEN_CHILDREN)' )

        parser.add_argument( '--initial-child-delay', action="store",
            metavar="MIN,MAX",
            **check_env_for_default( 'CENSERE_INITIAL_CHILD_DELAY', '350,700' ),
            help='Delay (sols) between relationship start and first child (CENSERE_INITIAL_CHILD_DELAY)' )

        parser.add_argument( '--initial-mission-lands', action="store",
            metavar="DATETIME",
            **check_env_for_default( 'CENSERE_INITIAL_MISSION_LANDS', '2024-01-01 00:00:00.000+00:00' ),
            help='Earth date that initial mission lands on Mars (CENSERE_INITIAL_MISSION_LANDS)' )

        parser.add_argument( '--limit', action="store",
            choices=['sols','population'],
            **check_env_for_default( 'CENSERE_LIMIT', 'population' ),
            help='Stop simmulation when we hit a time or population limit (CENSERE_LIMIT)' )

        parser.add_argument( '--limit-count', action="store",
            type=int,
            **check_env_for_default( 'CENSERE_LIMIT_COUNT', 1000 ),
            help='Stop simulation when we hit a time or population limit (CENSERE_LIMIT_COUNT)' )

        parser.add_argument( '--martian-gender-ratio', action="store",
            metavar="MALE,FEMALE",
            **check_env_for_default( 'CENSERE_MARTIAN_GENDER_RATIO', '50,50' ),
            help='Male:Female ratio for new born martians, Should add up to 100 (CENSERE_MARTIAN_GENDER_RATIO)' )

        parser.add_argument( '--orientation', action="store",
            metavar="HETROSEXUAL,HOMOSEXUAL,BISEXUAL",
            **check_env_for_default( 'CENSERE_OREINTATION', '90,6,4' ),
            help='Sexual orientation percentages, MUST add up to 100 (CENSERE_OREINTATION)' )

## Viewer-specific arguments
#
class ViewerOptions(CommonOptions):

    def register(self, parser):

        super().register(parser)
 
