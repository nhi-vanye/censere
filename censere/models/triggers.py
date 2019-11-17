
import logging

import sqlalchemy as SA

from config import Generator as thisApp

from .colonist import Colonist as Colonist
from .relationship import Relationship as Relationship
from .relationship import RelationshipEnum as RelationshipEnum

## 
# SQLAlchemy implements events at the application layer rather than
# native SQL triggers.
# Its convenient because we can use python to write "trigger" code
# at the cost of its not in the database.

##
# Does nothing - just logs the relationship status as it changes
#
@SA.event.listens_for(Colonist.state, "set", active_history=True, propagate=True)
def log_person_state_change(target, value, oldvalue, initiator):

    logging.debug( "Updating relationship state for {} {} ({}) {} -> {}".format( target.first_name, target.family_name, target.id, oldvalue, value))

    return True


##
# When a person dies we need to close out any PARTNER relationships
# they were in.
#
@SA.event.listens_for(Colonist.death_solday, "set", active_history=True, propagate=True)
def log_person_death(target, value, oldvalue, initiator):


    if value == oldvalue:
        return False

    logging.debug( "Updated death_solday for {} {} ({}) {} -> {}".format( target.first_name, target.family_name, target.id, oldvalue, value))

    session = thisApp.Session()

    #target.death_solday = value

    # When a person dies only their partner relationship ends
    # We don't remove any child/parent relationship links
    for r in session.query( Relationship ).filter( 
                SA.and_(
                    SA.or_(
                        Relationship.first == target.id,
                        Relationship.second == target.id
                    ),
                    Relationship.relationship == RelationshipEnum.partner,
                    Relationship.end_solday == 0
                )
            ):

        logging.info( "Relationship {} ended on {} due to death of {} {}".format( target.id, value, target.first_name, target.family_name))
        r.end_solday = value

    session.commit()

    return True

##
# If a relationship ends, then update the state of 
# each of the partners to `single` (if they are alive)
#
@SA.event.listens_for(Relationship.end_solday, "set", active_history=True)
def log_relationship_end(target, value, oldvalue, initiator):

    logging.debug( "Relationship ended between {} and {} {} -> {}".format( target.first, target.second, oldvalue, value))

    session = thisApp.Session()

    session.query( Colonist ).filter( 
            SA.and_(
                SA.or_(
                    Colonist.id == target.first,
                    Colonist.id == target.second
                ),
                Colonist.death_solday == 0,
            )
        ).update( { Colonist.state : 'single' } )

    session.commit()

    """
    # this resets the relationship state for any surviving people
    for user in session.query( Colonist ).filter( 
                SA.and_(
                    SA.or_(
                        Colonist.id == target.first,
                        Colonist.id == target.second
                    ),
                    Colonist.death_solday == 0,
                )
            ):

        logging.debug( 'Colonist {} {} = {}'.format( user.first_name, user.family_name, user.death_solday))
        user.state = 'single'

        session.commit()
"""
    return True

#@SA.event.listens_for(Relationship, "after_update")
def _update_person_state(mapper, connect, target):

    logging.info( "Relationship update {} started between {} and {} = {}".format( target.id, target.first, target.second, target.end_solday))

    if target.relationship != RelationshipEnum.partner:
        return

    if target.end_solday == 0:
        return

    session = thisApp.Session()
    # this resets the relationship state for any surviving people
    for user in session.query( Colonist ).filter( 
                SA.and_(
                    SA.or_(
                        Colonist.id == target.first,
                        Colonist.id == target.second
                    ),
                    Colonist.state == 'couple',
                )
            ):

        logging.debug( 'Colonist {} {} = {} {}'.format( user.first_name, user.family_name, user.death_solday, user.state))
 
    colonist_table = Colonist.__table__

    connect.execute(
            colonist_table.update().where( 
                SA.and_(
                    SA.or_(
                        colonist_table.c.id==target.first,
                        colonist_table.c.id==target.second
                    ),
                    colonist_table.c.death_solday == 0,
                )
            ).values(
                state='single'
            )
    )


##
# If a new relationship is created (new row added to table)
# then update each partner's state
# Only partner relationships.
@SA.event.listens_for(Relationship, "after_insert")
def _update_person_state(mapper, connect, target):

    if target.relationship != RelationshipEnum.partner:
        return

    logging.info( "Relationship {} started between {} and {}".format( target.id, target.first, target.second))

    colonist_table = Colonist.__table__

    connect.execute(
            colonist_table.update().where( 
                SA.or_(
                    colonist_table.c.id==target.first,
                    colonist_table.c.id==target.second
                )
            ).values(
                state='couple'
            )
    )


###
#
# additional triggers needed
#   update a person's productivity as the age/pregnant/maternity/paternity leave
#   update a person's resource consumption (oxygen etc) as they grow from birth
#   update habitation needs as families change
