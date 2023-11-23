## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

import apsw.bestpractice
import peewee
import playhouse.apsw_ext as APSW

apsw.bestpractice.apply(apsw.bestpractice.recommended)

from .local import mod as mod  # pylint: disable=unused-import

# I hate peewee's use of double quotes around tables and fields, the SQL looks ugly

# -use-memory-database requires APSW
class NoQuotesAPSW(APSW.APSWDatabase):
    quote = ( '', '' )

class NoQuotes(peewee.SqliteDatabase):
    quote = ( '', '' )

db = NoQuotesAPSW( None )

backup = NoQuotesAPSW( None )

import censere.models


##
# Each model (in models/) needs to have its table created
# so there should be an entry here.
def create_tables():

    censere.models.Demographic.create_table()
    censere.models.Event.create_table()
    censere.models.Relationship.create_table()
    censere.models.Population.create_table()
    censere.models.Settler.create_table()
    censere.models.Simulation.create_table()
    censere.models.Summary.create_table()
    censere.models.Commodity.create_table()
    censere.models.CommodityConsumer.create_table()
    censere.models.CommodityResevoir.create_table()
    censere.models.CommodityResevoirCapacity.create_table()
    censere.models.CommoditySupplier.create_table()
    censere.models.CommodityUsage.create_table()
