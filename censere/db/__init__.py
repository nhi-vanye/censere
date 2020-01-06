## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

import peewee

db = peewee.SqliteDatabase( None )

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
