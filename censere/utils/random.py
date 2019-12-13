## Wrapper around random routines to make it easier to re-implement


import numpy.random as NPRND

def seed( seed ):

    return NPRND.seed( seed )


# return a string of random bytes
# We use this rather than UUID so that
# we can get the same IDs if the same seed is used
def id():

    return NPRND.bytes(16).hex()


def random():

    return NPRND.random()


#
def randrange( start, stop ):

    return NPRND.randint( start, stop )

def randint( start, stop ):

    return randrange( start, stop + 1  )

def gauss( mean, sigma):

    return mean + ( NPRND.randn() * sigma )


def choice( lst):

    return NPRND.choice( lst )

def choices( lst, weights=None ):

    return NPRND.choice( lst, None, p=[ (i/100.0) for i in weights ] )
