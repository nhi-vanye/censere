# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 17:30:50 2019

@author: matej
"""

# Module gonverning the attributes of the colonists
# Updated to use SQLAlchemy 

import logging
import sqlalchemy as SA

from .base import Base as Base

##
# The Colonist is the base class for `Martian` or `Astronaut`
# As such it holds all the data fields
# The subclasses are expected to override any value for their
# class.
class Colonist(Base):

    __tablename__ = 'colonists'

    # Unique identifier for a person - names are not unique
    id = SA.Column(SA.String(36), primary_key=True)

    # allow the same database to be used for multple executions
    simulation = SA.Column(SA.String(36))

    # reproductive sex - currently expected to be either
    # `m` or `f`. In the future this could include `t`
    sex = SA.Column( SA.String(1) )

    # Lets treat them as human and give them names
    first_name = SA.Column(SA.String(32))
    family_name = SA.Column(SA.String(32))

    # record biological parents to avoid future close-relationships
    # TODO
    biological_father = SA.Column(SA.String(36) ) 
    biological_mother = SA.Column(SA.String(36) )

    # sexual orientation. acceptable values:
    #   m
    #   f
    #   mf
    # Only people of compatable orientations build families
    orientation = SA.Column( SA.String(3) )

    # Is the person `single` or a `couple`
    # TODO is `couple` the best word
    # Currently only `single` people can start a new family
    # That would need to change to handle extended families
    state = SA.Column( SA.String(10), default='single' )

    # obviously only valid for `f`
    pregnant = SA.Column( SA.Boolean(), default=False )

    # TODO 
    # how to track health state ???

    # Track Martian or Earther
    birth_location = SA.Column(SA.String(16))

    # all calculations are done using soldays with
    # conversions as needed (pregnany etc)
    birth_solday = SA.Column( SA.Integer )
    death_solday = SA.Column( SA.Integer, default=0 )

    # How productive is person ??
    productivity = SA.Column( SA.Integer, default=50 )

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
