
# -*- coding: utf-8 -*-
"""

@author: Richard Offer
"""

# Stores demographic results

from __future__ import division

import peewee
import playhouse.apsw_ext as APSW
import playhouse.signals

from censere.config import thisApp

import censere.db as DB
import censere.utils as UTILS

from .summary import Summary as Summary
from .settler import Settler as Settler
from .relationship import Relationship as Relationship
from .relationship import RelationshipEnum as RelationshipEnum

##
# Collect demographic details
#
class Demographic(playhouse.signals.Model):

    class Meta:
        database = DB.db

        table_name = 'demographics'

    # Unique identifier for the simulation
    simulation_id = APSW.UUIDField( )

    solday = APSW.IntegerField( )
    # All the calculations are based on soldays
    # but that is not very easy to plot
    # so provide a convertion to a datetime
    # based on inital_mission_lands date
    earth_datetime = APSW.DateTimeField()

    avg_annual_birth_rate = APSW.FloatField( null=True, default=0.0 )
    avg_annual_death_rate = APSW.FloatField( null=True, default=0.0 )

    avg_partnerships = APSW.FloatField( null=True, default=0.0 )
    num_partnerships_started = APSW.IntegerField( null=True, default=0 )
    num_partnerships_ended = APSW.IntegerField( null=True, default=0 )

    num_single_settlers = APSW.IntegerField( null=True, default=0 )
    num_partnered_settlers = APSW.IntegerField( null=True, default=0 )

    def initialize( self ):

        self.simulation_id = thisApp.simulation

        self.solday = thisApp.solday
        self.earth_datetime = thisApp.earth_time

        num_children_born = Settler.select().where(
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.birth_location == 'mars' ) &
            ( Settler.birth_solday > max( thisApp.solday - 668, 0 ) ) &
            ( Settler.birth_solday < thisApp.solday )
            ).count()

        num_deaths = Settler.select().where(
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.current_location == 'mars' ) &
            ( Settler.death_solday > max( thisApp.solday - 668, 0 ) ) &
            ( Settler.death_solday < thisApp.solday )
            ).count()

        year_start = Summary.get(
            ( Summary.simulation_id == thisApp.simulation ) &
            ( Summary.solday == max( thisApp.solday - (thisApp.solday % 668),0 ) )
            )

        year_end = Summary.get(
            ( Summary.simulation_id == thisApp.simulation ) &
            ( Summary.solday == thisApp.solday )
            )

        avg_population = year_start.population + int( 0.5 * ( year_end.population - year_start.population ) )

        # average are normally reported as rates per 1000 people
        if avg_population > 0 :
            self.avg_annual_birth_rate = ( num_children_born / avg_population ) * 1000.0
            self.avg_annual_death_rate = ( num_deaths / avg_population ) * 1000.0
        else:
            self.avg_annual_birth_rate = 0.0
            self.avg_annual_death_rate = 0.0


        self.num_partnerships_started = Relationship.select().where(
            ( Relationship.simulation_id == thisApp.simulation ) &
            ( Relationship.relationship == RelationshipEnum.partner ) &
            ( Relationship.begin_solday > max( thisApp.solday - 668, 0 ) ) &
            ( Relationship.begin_solday < thisApp.solday )
            ).count()

        self.num_partnerships_ended = Relationship.select().where(
            ( Relationship.simulation_id == thisApp.simulation ) &
            ( Relationship.relationship == RelationshipEnum.partner ) &
            ( Relationship.end_solday > max( thisApp.solday - 668, 0 ) ) &
            ( Relationship.end_solday < thisApp.solday )
            ).count()

        rel_year_start = Relationship.select().where(
            ( Relationship.simulation_id == thisApp.simulation ) &
            ( Relationship.relationship == RelationshipEnum.partner ) &
            ( Relationship.begin_solday < max( thisApp.solday - 668, 0 ) ) &
            (
                ( Relationship.end_solday == 0 ) |
                ( Relationship.end_solday < thisApp.solday )
            )
            ).count()

        rel_year_end = Relationship.select().where(
            ( Relationship.simulation_id == thisApp.simulation ) &
            ( Relationship.relationship == RelationshipEnum.partner ) &
            ( Relationship.begin_solday < thisApp.solday ) &
            (
                ( Relationship.end_solday == 0 ) |
                ( Relationship.end_solday < thisApp.solday )
            )
            ).count()

        self.avg_partnerships = rel_year_start + int( 0.5 * ( rel_year_end - rel_year_start ) )

        self.num_single_settlers = Settler.select().where(
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.state == 'single' ) &
            ( Settler.death_solday == 0 ) &
            ( Settler.birth_solday < (thisApp.solday - UTILS.years_to_sols(18) ) )
            ).count()

        self.num_partnered_settlers = Settler.select().where(
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.state == 'couple' ) &
            ( Settler.death_solday == 0 ) &
            ( Settler.birth_solday < (thisApp.solday - UTILS.years_to_sols(18) ) )
            ).count()

