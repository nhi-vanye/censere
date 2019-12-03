
##
# Convert from solsdays from landing to solyear + sol
# Add one to year so that land day is 1.1
def from_soldays( soldays ):

    (year, day) = divmod( soldays, 668 )

    return ( year + 1, day )
