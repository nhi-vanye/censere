"""
# Copyright (c) 2019 Richard Offer. All right reserved
#
# see LICENSE.md for license details

"""

# Stores summary results

import playhouse.apsw_ext as APSW
import playhouse.signals

import censere.db as DB


##
# Store Events for future invocation
#
class Event(playhouse.signals.Model):

    class Meta:
        database = DB.db

        table_name = 'events'

    # Unique identifier for the simulation
    simulation_id = APSW.UUIDField( )

    registered = APSW.IntegerField()

    runon = APSW.IntegerField( index=True, unique=False )
    # the callback will additionally be triggered when
    # solday % periodic == 0
    periodic = APSW.IntegerField( default = 0 )

    # allow ordering of callbacks within a single Sol
    # (low ones are executed first)
    priority = APSW.IntegerField( default=20)

    callback_func = APSW.CharField( 64 )

    idx = APSW.IntegerField( default=0 )

    args = APSW.TextField( default="{}" )
