# -*- coding: utf-8 -*-
"""

@author: Richard Offer
"""

# Stores summary results

import peewee
import playhouse.signals
import playhouse.apsw_ext as APSW

from censere.config import thisApp

import censere.db as DB

import censere.utils as UTILS

from .settler import Settler as Settler
from .settler import LocationEnum as LocationEnum
from .resources import CommodityResevoirCapacity as CommodityResevoirCapacity
from .resources import Resource as Resource

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
    simulation_id = APSW.UUIDField( )

    solday = APSW.IntegerField( )
    # All the calculations are based on soldays
    # but that is not very easy to plot
    # so provide convert to a datetime
    # based on inital_mission_lands date
    # BUT, pandas doesn't handle datetime after April 2262 - TODO
    earth_datetime = APSW.DateTimeField()

    adults = APSW.IntegerField( default=0 )
    children = APSW.IntegerField( default=0 )

    males = APSW.IntegerField( default=0 )
    females = APSW.IntegerField( default=0 )

    hetrosexual = APSW.IntegerField( default=0 )
    homosexual = APSW.IntegerField( default=0 )
    bisexual = APSW.IntegerField( default=0 )

    population = APSW.IntegerField( default=0 )

    singles = APSW.IntegerField( default=0 )
    couples = APSW.IntegerField( default=0 )

    deaths = APSW.IntegerField( default=0 )

    earth_born = APSW.IntegerField( default=0 )
    mars_born = APSW.IntegerField( default=0 )

    electricity_capacity = APSW.FloatField( default=0.0)
    water_capacity = APSW.FloatField( default=0.0)
    o2_capacity = APSW.FloatField( default=0.0)

    def initialize( self):

        adults = Settler.select().where( 
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.birth_solday < ( thisApp.solday - UTILS.years_to_sols(18) ) ) &
            ( Settler.death_solday == 0 )
        ).count()

        children = Settler.select().where( 
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.birth_solday >= ( thisApp.solday - UTILS.years_to_sols(18) ) ) &
            ( Settler.death_solday == 0 )
        ).count()

        singles = Settler.select().where( 
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.state == 'single' ) & 
            ( Settler.birth_solday < ( thisApp.solday - UTILS.years_to_sols(18) ) ) & 
            ( Settler.death_solday == 0 )
        ).count()

        couples = Settler.select().where( 
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.state == 'couple' ) & 
            ( Settler.birth_solday < ( thisApp.solday - UTILS.years_to_sols(18) ) ) & 
            ( Settler.death_solday == 0 )
        ).count()

        males = Settler.select().where( 
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.sex == 'm' ) & 
            ( Settler.death_solday == 0 )
        ).count()

        females = Settler.select().where( 
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.sex == 'f' ) & 
            ( Settler.death_solday == 0 )
        ).count()

        hetrosexual = Settler.select().where( 
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( ( ( Settler.sex == 'm' ) & 
                ( Settler.orientation == 'f' ) ) | 
            ( ( Settler.sex == 'f' ) & 
                ( Settler.orientation == 'm' ) ) ) &
            ( Settler.death_solday == 0 ) &
            ( Settler.birth_solday < ( thisApp.solday - UTILS.years_to_sols(18) ) )
        ).count()

        homosexual = Settler.select().where( 
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.sex == Settler.orientation ) & 
            ( Settler.death_solday == 0 ) &
            ( Settler.birth_solday < ( thisApp.solday - UTILS.years_to_sols(18) ) )
        ).count()

        bisexual = Settler.select().where( 
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.orientation == 'mf' ) & 
            ( Settler.death_solday == 0 ) &
            ( Settler.birth_solday < ( thisApp.solday - UTILS.years_to_sols(18) ) )
        ).count()

        deaths = Settler.select().where( 
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.death_solday != 0 )
        ).count()

        earth_born = Settler.select().where( 
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.birth_location == LocationEnum.Earth )
        ).count()

        mars_born = Settler.select().where( 
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.current_location == LocationEnum.Mars ) &
            ( Settler.birth_location == LocationEnum.Mars )
        ).count()

        try:
            electricity_stored = CommodityResevoirCapacity.select(
                peewee.fn.Sum(CommodityResevoirCapacity.capacity)
            ).where(
                ( CommodityResevoirCapacity.simulation_id == thisApp.simulation ) &
                ( CommodityResevoirCapacity.solday == thisApp.solday ) &
                ( CommodityResevoirCapacity.commodity == Resource.Electricity )
            ).scalar()
        except Exception as e:
            electricity_stored = 0.0

        try:
            water_stored = CommodityResevoirCapacity.select(
                peewee.fn.Sum(CommodityResevoirCapacity.capacity)
            ).where(
                ( CommodityResevoirCapacity.simulation_id == thisApp.simulation ) &
                ( CommodityResevoirCapacity.solday == thisApp.solday ) &
                ( CommodityResevoirCapacity.commodity == Resource.Water )
            ).scalar()
        except Exception as e:
            water_stored = 0.0

        try:
            o2_stored = CommodityResevoirCapacity.select(
                peewee.fn.Sum(CommodityResevoirCapacity.capacity)
            ).where(
                ( CommodityResevoirCapacity.simulation_id == thisApp.simulation ) &
                ( CommodityResevoirCapacity.solday == thisApp.solday ) &
                ( CommodityResevoirCapacity.commodity == Resource.O2 )
            ).scalar()
        except Exception as e:
            o2_stored = 0.0

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

        self.electricity_stored = electricity_stored
        self.water_stored = water_stored
        self.o2_stored = o2_stored

