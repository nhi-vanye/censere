# -*- coding: utf-8 -*-
"""

@author: Richard Offer
"""

# Stores details on a given simulation run.

import logging
import random
import uuid

import sqlalchemy as SA
import sqlalchemy.dialects.sqlite as SQLITE

from config import Generator as thisApp

from .base import Base as Base

##
# Store details about the simulation
# There will be additional details in the `summary` table 
# suitable for charting
class Simulation(Base):
    
    __tablename__ = 'simulations'

    # Unique identifier for the simulation
    id = SA.Column(SA.String(36), primary_key=True)

    # allow the same database to be used for multple executions
    begin_datetime = SA.Column(SQLITE.DATETIME())
    end_datetime = SA.Column(SQLITE.DATETIME())

    # how many days did the simulation run for
    soldays_elapsed = SA.Column( SA.Integer )

