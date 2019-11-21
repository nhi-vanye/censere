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
            help='Age range of arriving astronauts (CENSERE_ASTRONAUT_AGE_RANGE)' )

        parser.add_argument( '--limit', action="store",
            choices=['sols','population'],
            **check_env_for_default( 'CENSERE_LIMIT', 'population' ),
            help='Stop simmulation when we hit a time or population limit (CENSERE_LIMIT)' )

        parser.add_argument( '--limit-count', action="store",
            type=int,
            **check_env_for_default( 'CENSERE_LIMIT_COUNT', 1000 ),
            help='Stop simulation when we hit a time or population limit (CENSERE_LIMIT_COUNT)' )


## Viewer-specific arguments
#
class ViewerOptions(CommonOptions):

    def register(self, parser):

        super().register(parser)
 
