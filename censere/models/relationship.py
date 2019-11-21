
import peewee
import playhouse.signals

import censere.db as DB

class RelationshipEnum():
    partner = 1
    child = 2

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

