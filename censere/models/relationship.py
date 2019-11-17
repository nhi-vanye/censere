
import enum
import logging

import sqlalchemy as SA

from config import Generator as thisApp

from .base import Base as Base


class RelationshipEnum(enum.Enum):
    partner = 1
    child = 2

class Relationship( Base ):

    __tablename__ = 'relationships'

    id = SA.Column(SA.String(36), primary_key=True)

    first = SA.Column(SA.String(36), SA.ForeignKey('colonists.id'))
    second = SA.Column(SA.String(36), SA.ForeignKey('colonists.id'))

    relationship = SA.Column( SA.Enum(RelationshipEnum) )

    begin_solday = SA.Column( SA.Integer )
    end_solday = SA.Column( SA.Integer, default=0 )

    def __repr__(self):
        r"""
Provide a friendly representation of the object.
"""
        return "<Relationship('{} {} {}->{}')>".format(
                self.first, self.second, self.begin_solday, self.end_solday)
