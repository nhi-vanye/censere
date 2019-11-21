# -*- coding: utf-8 -*-
"""

@author: Richard Offer
"""

# Stores summary results

import peewee
import playhouse.signals

import censere.db as DB

##
# Collect summary details
#
# with the exception of deaths all values
# are for living people at the time they were recorded
#
# The orientation counts are for adults only - TODO
#
class Summary(playhouse.signals.Model):
    
    class Meta:
        database = DB.db

        table_name = 'summary'

    # Unique identifier for the simulation
    simulation_id = peewee.UUIDField( )

    solday = peewee.IntegerField( )

    adults = peewee.IntegerField( default=0 )
    children = peewee.IntegerField( default=0 )

    males = peewee.IntegerField( default=0 )
    females = peewee.IntegerField( default=0 )

    hetrosexual = peewee.IntegerField( default=0 )
    homosexual = peewee.IntegerField( default=0 )
    bisexual = peewee.IntegerField( default=0 )

    population = peewee.IntegerField( default=0 )

    singles = peewee.IntegerField( default=0 )
    couples = peewee.IntegerField( default=0 )

    deaths = peewee.IntegerField( default=0 )

    earth_born = peewee.IntegerField( default=0 )
    mars_born = peewee.IntegerField( default=0 )


    population = peewee.IntegerField( default=0 )

    singles = peewee.IntegerField( default=0 )
    couples = peewee.IntegerField( default=0 )

    deaths = peewee.IntegerField( default=0 )

    earth_born = peewee.IntegerField( default=0 )
    mars_born = peewee.IntegerField( default=0 )

