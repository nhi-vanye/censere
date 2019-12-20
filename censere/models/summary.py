# -*- coding: utf-8 -*-
"""

@author: Richard Offer
"""

# Stores summary results

import peewee
import playhouse.signals

from censere.config import Generator as thisApp

import censere.db as DB

import censere.utils as UTILS

from .settler import Settler as Settler
from .settler import LocationEnum as LocationEnum

##
# Collect summary details
#
# with the exception of deaths all values
# are for living people at the time they were recorded
#
# The orientation counts are for adults only - TODO
#
class Summary(playhouse.signals.Model):
    
    class Meta:
        database = DB.db

        table_name = 'summary'

    # Unique identifier for the simulation
    simulation_id = peewee.UUIDField( )

    solday = peewee.IntegerField( )
    # All the calculations are based on soldays
    # but that is not very easy to plot
    # so provide convert to a datetime
    # based on inital_mission_lands date
    earth_datetime = peewee.DateTimeField()

    adults = peewee.IntegerField( default=0 )
    children = peewee.IntegerField( default=0 )

    males = peewee.IntegerField( default=0 )
    females = peewee.IntegerField( default=0 )

    hetrosexual = peewee.IntegerField( default=0 )
    homosexual = peewee.IntegerField( default=0 )
    bisexual = peewee.IntegerField( default=0 )

    population = peewee.IntegerField( default=0 )

    singles = peewee.IntegerField( default=0 )
    couples = peewee.IntegerField( default=0 )

    deaths = peewee.IntegerField( default=0 )

    earth_born = peewee.IntegerField( default=0 )
    mars_born = peewee.IntegerField( default=0 )

    avg_annual_birth_rate = peewee.FloatField( null=True )
    avg_annual_death_rate = peewee.FloatField( null=True )


    def initialize( self):

        adults = Settler.select().where( 
            ( Settler.simulation == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.birth_solday < ( thisApp.solday - UTILS.years_to_sols(18) ) ) &
            ( Settler.death_solday == 0 )
        ).count()

        children = Settler.select().where( 
            ( Settler.simulation == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.birth_solday >= ( thisApp.solday - UTILS.years_to_sols(18) ) ) &
            ( Settler.death_solday == 0 )
        ).count()

        singles = Settler.select().where( 
            ( Settler.simulation == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.state == 'single' ) & 
            ( Settler.birth_solday < ( thisApp.solday - UTILS.years_to_sols(18) ) ) & 
            ( Settler.death_solday == 0 )
        ).count()

        couples = Settler.select().where( 
            ( Settler.simulation == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.state == 'couple' ) & 
            ( Settler.birth_solday < ( thisApp.solday - UTILS.years_to_sols(18) ) ) & 
            ( Settler.death_solday == 0 )
        ).count()

        males = Settler.select().where( 
            ( Settler.simulation == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.sex == 'm' ) & 
            ( Settler.death_solday == 0 )
        ).count()

        females = Settler.select().where( 
            ( Settler.simulation == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.sex == 'f' ) & 
            ( Settler.death_solday == 0 )
        ).count()

        hetrosexual = Settler.select().where( 
            ( Settler.simulation == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( ( ( Settler.sex == 'm' ) & 
                ( Settler.orientation == 'f' ) ) | 
            ( ( Settler.sex == 'f' ) & 
                ( Settler.orientation == 'm' ) ) ) &
            ( Settler.death_solday == 0 ) &
            ( Settler.birth_solday < ( thisApp.solday - UTILS.years_to_sols(18) ) )
        ).count()

        homosexual = Settler.select().where( 
            ( Settler.simulation == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.sex == Settler.orientation ) & 
            ( Settler.death_solday == 0 ) &
            ( Settler.birth_solday < ( thisApp.solday - UTILS.years_to_sols(18) ) )
        ).count()

        bisexual = Settler.select().where( 
            ( Settler.simulation == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.orientation == 'mf' ) & 
            ( Settler.death_solday == 0 ) &
            ( Settler.birth_solday < ( thisApp.solday - UTILS.years_to_sols(18) ) )
        ).count()

        deaths = Settler.select().where( 
            ( Settler.simulation == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.death_solday != 0 )
        ).count()

        earth_born = Settler.select().where( 
            ( Settler.simulation == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.birth_location == LocationEnum.Earth )
        ).count()

        mars_born = Settler.select().where( 
            ( Settler.simulation == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.birth_location == LocationEnum.Mars )
        ).count()

        self.simulation_id = thisApp.simulation

        self.solday = thisApp.solday
        self.earth_datetime = thisApp.earth_time
        self.adults = adults
        self.children = children

        self.males = males
        self.females = females

        self.hetrosexual = hetrosexual
        self.homosexual = homosexual
        self.bisexual = bisexual

        self.population = adults + children

        self.singles = singles
        self.couples = couples

        self.deaths = deaths

        self.earth_born = earth_born
        self.mars_born = mars_born

