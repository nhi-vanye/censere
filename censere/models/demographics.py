
# -*- coding: utf-8 -*-
"""

@author: Richard Offer
"""

# Stores demographic results

from __future__ import division

import peewee
import playhouse.signals

from censere.config import Generator as thisApp

import censere.db as DB

from .summary import Summary as Summary
from .settler import Settler as Settler

##
# Collect demographic details
#
class Demographic(playhouse.signals.Model):

    class Meta:
        database = DB.db

        table_name = 'demographics'

    # Unique identifier for the simulation
    simulation_id = peewee.UUIDField( )

    solday = peewee.IntegerField( )
    # All the calculations are based on soldays
    # but that is not very easy to plot
    # so provide a convertion to a datetime
    # based on inital_mission_lands date
    earth_datetime = peewee.DateTimeField()

    avg_annual_birth_rate = peewee.FloatField( null=True )
    avg_annual_death_rate = peewee.FloatField( null=True )

    def initialize( self ):

        self.simulation_id = thisApp.simulation

        self.solday = thisApp.solday
        self.earth_datetime = thisApp.earth_time

        num_children_born = Settler.select().where(
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.birth_solday > max( thisApp.solday - 668, 0 ) ) &
            ( Settler.birth_solday < thisApp.solday )
            ).count()

        num_deaths = Settler.select().where(
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.death_solday > max( thisApp.solday - 668, 0 ) ) &
            ( Settler.death_solday < thisApp.solday )
            ).count()

        year_start = Summary.get(
            ( Summary.simulation_id == thisApp.simulation ) &
            ( Summary.solday == max( thisApp.solday - 668, 0 ) )
            )

        year_end = Summary.get(
            ( Summary.simulation_id == thisApp.simulation ) &
            ( Summary.solday == thisApp.solday )
            )

        avg_population = year_start.population + int( 0.5 * ( year_end.population - year_start.population ) )

        # average are normally reported as rates per 1000 people
        self.avg_annual_birth_rate = ( num_children_born / avg_population ) * 1000.0
        self.avg_annual_death_rate = ( num_deaths / avg_population ) * 1000.0
