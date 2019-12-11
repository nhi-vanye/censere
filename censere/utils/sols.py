## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

##
# Convert from solsdays from landing to solyear + sol
# Add one to year so that land day is 1.1
def from_soldays( soldays ):

    (year, day) = divmod( soldays, 668 )

    return ( year + 1, day )
