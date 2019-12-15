## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details
#
## Wrapper around random routines to make it easier to re-implement


import numpy.random as NPRND

def seed( seed ):

    return NPRND.seed( seed )


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


## return a random number between start and stop
#
# Return a random integer N such that a <= N < b.
#
def randrange( start, stop ):

    return NPRND.randint( start, stop )

##
#
# Return a random integer N such that a <= N <= b. Alias for randrange(a, b+1)
#
def randint( start, stop ):

    if start == stop:
        return start

    return randrange( start, stop + 1  )

def gauss( mean, sigma):

    return mean + ( NPRND.randn() * sigma )


def choice( lst):

    return NPRND.choice( lst )

def choices( lst, weights=None ):

    return NPRND.choice( lst, None, p=[ (i/100.0) for i in weights ] )
