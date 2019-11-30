

# Convenient function to map from earth years
# to the number of sols - useful for mapping ages etc
def years_to_sols(years):
    return int( years * 365.25 * 1.02749125)
