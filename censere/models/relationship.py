
import peewee
import playhouse.signals

import censere.db as DB

class RelationshipEnum():
    partner = 0
    parent = 1
    # These are generational
    grandparent = 2
    great_grandparent = 3
    great_great_grandparent = 4
    great_great_great_grandparent = 5
    great_great_great_great_grandparent = 6
    great_great_great_great_great_grandparent = 7
    great_great_great_great_great_great_grandparent = 8
    great_great_great_great_great_great_great_grandparent = 9
    great_great_great_great_great_great_great_great_grandparent = 10

class Relationship( playhouse.signals.Model ):

    class Meta:
        database = DB.db

        table_name = 'relationships'

    def __repr__(self):
        return "{} {} <-> {}".format( self.relationship_id, self.first, self.second ) 

    relationship_id = peewee.UUIDField( unique=True)

    # 
    first = peewee.UUIDField()
    second = peewee.UUIDField()

    relationship = peewee.IntegerField()

    begin_solday = peewee.IntegerField()
    end_solday = peewee.IntegerField( default=0 )

