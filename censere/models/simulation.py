# -*- coding: utf-8 -*-
"""

@author: Richard Offer
"""

# Stores details on a given simulation run.

import peewee
import playhouse.signals

import censere.db as DB


##
# Store details about the simulation
# There will be additional details in the `summary` table 
# that are suitable for charting
class Simulation(playhouse.signals.Model):
    
    class Meta:
        database = DB.db

        table_name = 'simulations'

    # Unique identifier for the simulation
    simulation_id = peewee.UUIDField( unique=True)

    # record the wall time we ran the simulation
    begin_datetime = peewee.DateTimeField( )
    end_datetime = peewee.DateTimeField( null=True )

    limit = peewee.CharField( )
    limit_count = peewee.IntegerField( )

    # how many days did the simulation run for
    soldays_elapsed = peewee.IntegerField( null=True)

