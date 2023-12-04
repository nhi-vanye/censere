## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

# Stores details on a given simulation run.

import playhouse.apsw_ext as APSW
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
    simulation_id = APSW.UUIDField( unique=True)

    me_earthtime = APSW.DateTimeField( null=True)
    human_mission_lands = APSW.IntegerField( null=True)
    initial_human_mission_lands = APSW.DateTimeField( null=True)

    # record the wall time we ran the simulation
    begin_datetime = APSW.DateTimeField( )
    end_datetime = APSW.DateTimeField( null=True )

    limit_type = APSW.CharField( )
    limit_count = APSW.IntegerField( )

    # how many days did the simulation run for
    mission_ends = APSW.DateTimeField( null=True )

    final_soldays = APSW.IntegerField( null=True)
    final_population = APSW.IntegerField( null=True)

    ## record arguments used to configure simulation
    args = APSW.TextField( null=True )

    # add a column for storing simulation notes
    # Nothing in generator will add to this column, its for
    # storing descriptive text found during analysis
    # include a default to avoid storing NULLs which hamper graphing
    notes = APSW.TextField( null=True, default='' )

    random_seed = APSW.IntegerField( null=True )
    random_state = APSW.TextField( null=True )
