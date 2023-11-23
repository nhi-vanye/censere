# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 17:30:50 2019

@author: matej
Completely re-written November 2019: Richard Offer
"""

# Module governing the attributes of the settlers
# Updated to use an ORM for storage in database

import playhouse.apsw_ext as APSW
import playhouse.signals

import censere.db as DB


class LocationEnum():
    other = 'other'
    Earth = 'earth'
    Mars = 'mars'
    space = 'space'


##
# The Settler is the base class for `Martian` or `Astronaut`
# As such it holds all the data fields
# The subclasses are expected to override any value for their
# class.
class Settler(playhouse.signals.Model):

    class Meta:
        database = DB.db

        table_name = 'settlers'

        indexes = (
            (('simulation_id', 'settler_id'), True),
        )

    ## provide a internal representation function
    # to make debugging easier
    def __repr__(self):
        return "{} {} ({})".format( self.first_name, self.family_name, self.settler_id )

    # allow the same database to be used for multple executions
    simulation_id = APSW.UUIDField( index=True, unique=False )

    # Unique identifier for a person - names are not unique
    settler_id = APSW.CharField( 32, index=True, unique=False )

    # reproductive sex - currently expected to be either
    # `m` or `f`. In the future this could include `t`
    sex = APSW.CharField( 1 )

    # Lets treat them as human and give them names
    first_name = APSW.CharField( 32 )
    family_name = APSW.CharField( 32 )

    # record biological parents to avoid future close-relationships
    # TODO - use this data
    # These cannot be foreign keys, because there may not be a Settler row with
    # that id. Think astronaut whose parents are still on Earth
    biological_father = APSW.CharField(32)
    biological_mother = APSW.CharField(32)

    # sexual orientation. acceptable values:
    #   m
    #   f
    #   mf
    # Only people of compatable orientations build families
    orientation = APSW.CharField(3)

    # Is the person `single` or a `couple`
    # TODO is `couple` the best word ?
    # Currently only `single` people can start a new family
    # That would need to change to handle extended families
    state = APSW.CharField( 8, default='single' )

    # obviously only valid for `f`
    pregnant = APSW.BooleanField( default=False )

    # TODO
    # how to track health state ???

    # Track Martian or Earther
    birth_location = APSW.CharField( 8 )
    # and where they are now
    current_location = APSW.CharField( 8 )

    # all calculations are done using soldays with
    # conversions as needed (pregnany etc)
    birth_solday = APSW.IntegerField( )
    death_solday = APSW.IntegerField( default=0 )

    cohort = APSW.IntegerField( default=0 )

    # How productive is person ??
    productivity = APSW.IntegerField( default=50 )
