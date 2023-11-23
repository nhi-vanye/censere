## Copyright (c) 2019 Richard Offer. All right reserved.
#
# see LICENSE.md for license details

import playhouse.apsw_ext as APSW
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

        indexes = (
            (('simulation_id', 'relationship_id'), True),
        )

    def __repr__(self):
        return "{} {} <-> {}".format( self.relationship_id, self.first, self.second )

    simulation_id = APSW.UUIDField()

    relationship_id = APSW.CharField( 32 )

    # These are not marked as foreign keys to allow relationships to people
    # that do not exist in the database
    # i.e. parents of astronauts
    #
    # TODO - we could tighten it up and make `first` a foreign key
    first = APSW.UUIDField()
    second = APSW.UUIDField()

    relationship = APSW.IntegerField()

    begin_solday = APSW.IntegerField()
    end_solday = APSW.IntegerField( default=0 )
