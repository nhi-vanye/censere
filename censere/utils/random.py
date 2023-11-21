## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details
#
## Wrapper around random routines to make it easier to re-implement

import logging

import numpy.random as NPRND

import censere.utils as UTILS

LOGGER = logging.getLogger("c.u.random")
DEVLOG = logging.getLogger("d.devel")

# Life table for the total population: United States, 2006
cdc_2006 = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
    51,
    52,
    53,
    54,
    55,
    56,
    57,
    58,
    59,
    60,
    61,
    62,
    63,
    64,
    65,
    66,
    67,
    68,
    69,
    70,
    71,
    72,
    73,
    74,
    75,
    76,
    77,
    78,
    79,
    80,
    81,
    82,
    83,
    84,
    85,
    86,
    87,
    88,
    89,
    90,
    91,
    92,
    93,
    94,
    95,
    96,
    97,
    98,
    99,
    100,
]

# 4.696378 is the sum of all probablilities
#
cdc_2006_weights = [
    0.006713 / 4.696378 ,
    0.000444 / 4.696378,
    0.000300 / 4.696378,
    0.000216 / 4.696378,
    0.000179 / 4.696378,
    0.000168 / 4.696378,
    0.000156 / 4.696378,
    0.000143 / 4.696378,
    0.000125 / 4.696378,
    0.000103 / 4.696378,
    0.000086 / 4.696378,
    0.000088 / 4.696378,
    0.000125 / 4.696378,
    0.000206 / 4.696378,
    0.000317 / 4.696378,
    0.000438 / 4.696378,
    0.000552 / 4.696378,
    0.000657 / 4.696378,
    0.000747 / 4.696378,
    0.000825 / 4.696378,
    0.000905 / 4.696378,
    0.000983 / 4.696378,
    0.001033 / 4.696378,
    0.001049 / 4.696378,
    0.001038 / 4.696378,
    0.001019 / 4.696378,
    0.001006 / 4.696378,
    0.000998 / 4.696378,
    0.001002 / 4.696378,
    0.001018 / 4.696378,
    0.001042 / 4.696378,
    0.001072 / 4.696378,
    0.001113 / 4.696378,
    0.001156 / 4.696378,
    0.001212 / 4.696378,
    0.001276 / 4.696378,
    0.001355 / 4.696378,
    0.001456 / 4.696378,
    0.001585 / 4.696378,
    0.001739 / 4.696378,
    0.001903 / 4.696378,
    0.002077 / 4.696378,
    0.002268 / 4.696378,
    0.002479 / 4.696378,
    0.002706 / 4.696378,
    0.002943 / 4.696378,
    0.003190 / 4.696378,
    0.003453 / 4.696378,
    0.003741 / 4.696378,
    0.004057 / 4.696378,
    0.004405 / 4.696378,
    0.004778 / 4.696378,
    0.005166 / 4.696378,
    0.005554 / 4.696378,
    0.005939 / 4.696378,
    0.006335 / 4.696378,
    0.006760 / 4.696378,
    0.007234 / 4.696378,
    0.007796 / 4.696378,
    0.008470 / 4.696378,
    0.009282 / 4.696378,
    0.010204 / 4.696378,
    0.011178 / 4.696378,
    0.012118 / 4.696378,
    0.013024 / 4.696378,
    0.013999 / 4.696378,
    0.014995 / 4.696378,
    0.016161 / 4.696378,
    0.017527 / 4.696378,
    0.019109 / 4.696378,
    0.020890 / 4.696378,
    0.022925 / 4.696378,
    0.025280 / 4.696378,
    0.027972 / 4.696378,
    0.030997 / 4.696378,
    0.034386 / 4.696378,
    0.038027 / 4.696378,
    0.042036 / 4.696378,
    0.046447 / 4.696378,
    0.051297 / 4.696378,
    0.056623 / 4.696378,
    0.062465 / 4.696378,
    0.068867 / 4.696378,
    0.075871 / 4.696378,
    0.083524 / 4.696378,
    0.091872 / 4.696378,
    0.100962 / 4.696378,
    0.110842 / 4.696378,
    0.121558 / 4.696378,
    0.133155 / 4.696378,
    0.145675 / 4.696378,
    0.159156 / 4.696378,
    0.173631 / 4.696378,
    0.189127 / 4.696378,
    0.205661 / 4.696378,
    0.223242 / 4.696378,
    0.241869 / 4.696378,
    0.261527 / 4.696378,
    0.282188 / 4.696378,
    0.303810 / 4.696378,
    1.0000 / 4.6963780
]


def seed( seed ):

    return NPRND.seed( seed )


def set_state( st ):

    return NPRND.set_state( st )

def get_state( ):

    return NPRND.get_state( )

# return a string of random bytes
# We use this rather than UUID so that
# we can get the same IDs if the same seed is used
#
# uuid.uuid() uses the os.urandom() and can't be replayed.
#
def id():

    return NPRND.bytes(16).hex()


def random():

    return NPRND.random()

def randf(low:float, high:float) -> float:

    return ( (high - low ) * NPRND.random_sample() ) + low


## return a random integer between start and stop
#
# Return a random integer N such that a <= N < b.
#
def randrange( start:int, stop:int ) -> int:

    return NPRND.randint( start, stop )

##
#
# Return a random integer N such that a <= N <= b. Alias for randrange(a, b+1)
#
def randint( start:int, stop:int ) -> int:

    if start == stop:
        return start

    return randrange( start, stop + 1  )

def normal( mean:float, sigma:float) -> float:

    return NPRND.normal( mean, sigma )

def triangle( minimum, peak, maximum):
    "works with int or float"

    return NPRND.triangular( minimum, peak, maximum )

def binomial( probability:float) -> bool:

    return NPRND.binomial( 1, probability, 1 ) == 1

def choice( lst:list):

    return NPRND.choice( lst )

def choices( lst:list, weights=None ):

    return NPRND.choice( lst, None, p=[ (i/100.0) for i in weights ] )

def life_expectancy():

    return NPRND.choice( cdc_2006, None, p=cdc_2006_weights )


##
# tables: prefix is only valid for life-expectancy values
#
# Difference between randint and randrange is that randint only returns int
# and handles the case where MIN == MAX, randrange will error in that case
# TODO
#   * handle sexes life expectancy independently
# 
def parse_random_value( key, default_value=None, key_in_earth_years=False ):

    if key == "":
        return default_value

    val = key.split(":")

    value = default_value


    if val[0] == "cdc":
        value = life_expectancy()

    elif val[0] == "triangular" or val[0] == "triangle" :

        values = [ float(i) for i in val[1].split(",") ]
        value = triangle( values[0], values[1], values[2] )

    elif val[0] == "normal":
        values = [ float(i) for i in val[1].split(",") ]
        value = normal( values[0], values[1] )

    elif val[0] == "binomial":
        values = [ float(i) for i in val[1].split(",") ]
        value = binomial( values[0] )

    elif val[0] == "randint":

        values = [ int(i) for i in val[1].split(",") ]
        value = randint( values[0], values[1] )

    elif val[0] == "randrange":

        values =  [float(i) for i in val[1].split(",") ]
        value = randrange( values[0], values[1] )

    elif val[0] == "half":

        values = [ float(i) for i in val[1].split(",") ]

        r = random()

        if r < 0.5:
            value = ( values[0] ) + ( values[1] * random() )
        elif r < 0.75:
            value = ( values[0] + ( values[1] ) ) + ( values[1] * random() )
        elif r < 0.875:
            value = ( values[0] + ( values[1] * 2 ) ) + ( values[1] * random() )
        elif r < 0.925:
            value = ( values[0] + ( values[1] * 3 ) ) + ( values[1] * random() )
        elif r < 0.9625:
            value = ( values[0] + ( values[1] * 4 ) ) + ( values[1] * random() )
        elif r < 0.98125:
            value = ( values[0] + ( values[1] * 5 ) ) + ( values[1] * random() )
        elif r < 0.990625:
            value = ( values[0] + ( values[1] * 6 ) ) + ( values[1] * random() )
        elif r < 0.9953125:
            value = ( values[0] + ( values[1] * 7 ) ) + ( values[1] * random() )
        else:
            value = ( values[0] + ( values[1] * 8 ) ) + ( values[1] * random() )
 
    else:

        LOGGER.fatal( 'Invalid value %s', key )


    if key_in_earth_years:

        return UTILS.years_to_sols( value )

    return value
