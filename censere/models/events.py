"""
# Copyright (c) 2019 Richard Offer. All right reserved
#
# see LICENSE.md for license details

"""

# Stores summary results

import peewee
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
    simulation_id = peewee.UUIDField( )

    registered = peewee.IntegerField()

    when = peewee.IntegerField( index=True, unique=False )
    # the callback will additionally be triggered when
    # solday % periodic == 0
    periodic = peewee.IntegerField( default = 0 )

    # allow ordering of callbacks within a single Sol
    # (low ones are executed first)
    order = peewee.IntegerField( default=20)

    callback_func = peewee.CharField( 64 )

    idx = peewee.IntegerField( default=0 )

    args = peewee.TextField( default="{}" )


