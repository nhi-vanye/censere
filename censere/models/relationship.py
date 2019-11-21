
import enum
import logging

import peewee
import playhouse.signals

import db

from config import Generator as thisApp

from .colonist import Colonist as Colonist


class RelationshipEnum():
    partner = 1
    child = 2

class Relationship( playhouse.signals.Model ):

    class Meta:
        database = db.db

        table_name = 'relationships'

    def __repr__(self):
        return "{} {} <-> {}".format( self.relationship_id, self.first, self.second ) 

    relationship_id = peewee.UUIDField( unique=True)

    # TODO - make these foreign key or not ?
    first = peewee.UUIDField()
    second = peewee.UUIDField()
    # 
    #first = peewee.ForeignKeyField(Colonist, field="colonist_id", backref='partner')
    #second = peewee.ForeignKeyField(Colonist, field="colonist_id", backref='partner')

    relationship = peewee.IntegerField()

    begin_solday = peewee.IntegerField()
    end_solday = peewee.IntegerField( default=0 )

