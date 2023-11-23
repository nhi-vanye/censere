
# -*- coding: utf-8 -*-
"""

@author: Richard Offer
"""

# Stores demographic results

import numpy
import playhouse.apsw_ext as APSW
import playhouse.signals

import censere.db as DB
from censere.config import thisApp

from .settler import Settler as Settler


##
# Collect population details
#
class Population(playhouse.signals.Model):

    class Meta:
        database = DB.db

        table_name = 'populations'

    # Unique identifier for the simulation
    simulation_id = APSW.UUIDField( )

    solday = APSW.IntegerField( )
    # All the calculations are based on soldays
    # but that is not very easy to plot
    # so provide a convertion to a datetime
    # based on inital_mission_lands date
    earth_datetime = APSW.DateTimeField()


    bucket = APSW.CharField( 8 )
    sol_years = APSW.IntegerField( 8 )
    sex = APSW.CharField( 1 )
    value = APSW.IntegerField( )

def get_population_histogram( ):


    q = Settler.select(
            thisApp.solday - Settler.birth_solday,
            Settler.sex
        ).where(
            ( Settler.simulation_id == thisApp.simulation ) &
            ( Settler.death_solday == 0 )
        ).tuples()

    f = []
    m = []

    # convert from soldays to solyears
    # a solyear is still close to twice as long as an earth year...
    for i in q.execute():

        if i[1] == 'm':
            m.append( int( i[0] / 668.0 ) )
        else:
            f.append( int( i[0] / 668.0 ) )


    # don't forget these are solyears, so 50 is _old_
    bins = [0,5,10,15,20,25,30,35,40,45,50]
    males = numpy.histogram( m, bins=bins )
    females = numpy.histogram( f, bins=bins )

    return ( males, females )
