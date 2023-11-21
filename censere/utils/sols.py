## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

##
# Convert from solsdays from landing to solyear + sol
# Add one to year so that land day is 1.1
# much like BCE / CE there is no year 0
def from_soldays( soldays ):

    (year, day) = divmod( abs(soldays), 668 )

    if soldays < 0:
        return ( -1 * (year+1), day )
    else:
        return ( year + 1, day )
