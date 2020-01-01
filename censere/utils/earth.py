## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details


# Convenient function to map from earth years
# to the number of sols - useful for mapping ages etc
def years_to_sols(years):
    return int( years * 365.25 * 1.02749125)

# Convert sols to earth years
def sols_to_age(sols):

    return int( sols / ( 1.02749125 * 365.25 ) )
