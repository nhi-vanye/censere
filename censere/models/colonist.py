# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 17:30:50 2019

@author: matej
"""

# Module governing the attributes of the colonists
# Updated to use an ORM for storage in database 

import peewee
import playhouse.signals

import censere.db as DB

##
# The Colonist is the base class for `Martian` or `Astronaut`
# As such it holds all the data fields
# The subclasses are expected to override any value for their
# class.
#class Colonist(playhouse.signals.Model):
class Colonist(playhouse.signals.Model):

    class Meta:
        database = DB.db

        table_name = 'colonists'


    ## provide a internal representation function
    # to make debugging easeir
    def __repr__(self):
        return "{} {} ({})".format( self.first_name, self.family_name, self.colonist_id ) 

    # Unique identifier for a person - names are not unique
    colonist_id = peewee.UUIDField( unique=True )

    # allow the same database to be used for multple executions
    simulation = peewee.UUIDField()

    # reproductive sex - currently expected to be either
    # `m` or `f`. In the future this could include `t`
    sex = peewee.CharField( 1 )

    # Lets treat them as human and give them names
    first_name = peewee.CharField( 32 )
    family_name = peewee.CharField( 32 )

    # record biological parents to avoid future close-relationships
    # TODO - use this data
    # These cannot be foreign keys, because there may not be a Colonist row with
    # that id. Think astronaut whose parents are still on Earth
    biological_father = peewee.UUIDField()
    biological_mother = peewee.UUIDField()

    # sexual orientation. acceptable values:
    #   m
    #   f
    #   mf
    # Only people of compatable orientations build families
    orientation = peewee.CharField(3)

    # Is the person `single` or a `couple`
    # TODO is `couple` the best word ?
    # Currently only `single` people can start a new family
    # That would need to change to handle extended families
    state = peewee.CharField( 8, default='single' )

    # obviously only valid for `f`
    pregnant = peewee.BooleanField( default=False )

    # TODO 
    # how to track health state ???

    # Track Martian or Earther
    birth_location = peewee.CharField(16)

    # all calculations are done using soldays with
    # conversions as needed (pregnany etc)
    birth_solday = peewee.IntegerField( )
    death_solday = peewee.IntegerField( default=0 )

    # How productive is person ??
    productivity = peewee.IntegerField( default=50 )

    """
    def getWorkHours(self):
        ageYrs = self.getAge()
        if (ageYrs < self.params.getCOLONIST_DEPENDENT_AGE()):
            return self.params.getCOLONIST_DEPENDENT_WORK()
        elif (ageYrs < self.params.getCOLONIST_PRODUCTIVE_AGE()):
            return self.params.getCOLONIST_NONPROD_WORK()
        elif (ageYrs < self.params.getCOLONIST_ELDERLY_AGE()):
            return self.params.getCOLONIST_PRODUCTIVE_WORK()
        else:
            return self.params.getCOLONIST_ELDERLY_WORK()
"""
