
import peewee

from config import Generator as thisApp


db = peewee.SqliteDatabase( None )

import models


def create_tables():

    models.Astronaut.create_table()
    models.Relationship.create_table()
    models.Simulation.create_table()
    models.Summary.create_table()
