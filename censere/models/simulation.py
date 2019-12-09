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

    initial_mission_lands = peewee.DateTimeField()

    # record the wall time we ran the simulation
    begin_datetime = peewee.DateTimeField( )
    end_datetime = peewee.DateTimeField( null=True )

    limit = peewee.CharField( )
    limit_count = peewee.IntegerField( )

    # how many days did the simulation run for
    mission_ends = peewee.DateTimeField( null=True )

    final_soldays = peewee.IntegerField( null=True)
    final_population = peewee.IntegerField( null=True)

    ## record arguments used to configure simulation
    args = peewee.BlobField( null=True )

    # add a column for storing simulation notes
    # Nothing in generator will add to this column, its for
    # storing descriptive text found during analysis
    notes = peewee.TextField( null=True )

