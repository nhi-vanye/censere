
# -*- coding: utf-8 -*-
"""

@author: Richard Offer
"""

# Module governing the usage of resources

import peewee
import playhouse.signals

import censere.db as DB


##
# Holds the running resource usage...
class ResourceUsage(playhouse.signals.Model):

    class Meta:
        database = DB.db

        table_name = 'resource_usage'

        indexes = (
            (('simulation_id', 'resource_id'), True),
        )

    ## provide a internal representation function
    # to make debugging easier
    def __repr__(self):
        return "{} ({})".format( self.resource_type, self.resource_id )

    # allow the same database to be used for multple executions
    simulation_id = peewee.UUIDField( index=True, unique=False )

    # Unique identifier for a single physical resource
    # for example a battery, or single CO2 scrubber
    resource_id = peewee.CharField( 32, index=True, unique=False )

    # human name to make it easier to track
    resource_name = peewee.CharField( 32 )

    resource_type = peewee.CharField( 8 )

    resource_unit = peewee.CharField(8)

    sol = peewee.IntegerField( )

    # per Sol usage
    supply = peewee.FloatField( )
    demand = peewee.FloatField( )

    running_total == peewee.FloatField( default = 0.0 )
