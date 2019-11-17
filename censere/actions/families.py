
import logging
import uuid

import sqlalchemy as SA

from config import Generator as thisApp

import models

##
# Make a single new family out of two singles
# the caller is responsible for calling this at
# appropriate times...
def make( solday, solyear, sol ):

    logging.info( '{}.{} ({}) Making a new family'.format( solyear, sol, solday) )

    p1 = SA.orm.aliased(models.Colonist)
    p2 = SA.orm.aliased(models.Colonist)

    session = thisApp.Session()

    # TODO how to avoid "incest" ?
    # - both persons must be single
    for user1, user2 in session.query( p1, p2 ).filter( 
        SA.and_(
            p1.id != p2.id,
            p1.state == 'single',
            p2.state == 'single',
            p1.orientation.contains(p2.sex),
            p2.orientation.contains(p1.sex),
            p1.birth_solday < solday - ( 18 * 365.25 * 1.02749125 ),
            p2.birth_solday < solday - ( 18 * 365.25 * 1.02749125 ),
            p1.death_solday == 0,
            p2.death_solday == 0,
            p1.simulation == p2.simulation # make sure we're in the same execution run
        ) ).order_by( SA.sql.functions.random() ).limit(1):

        # to improve perfomance we mark the users as being in a relatiosnhp here
        # rather than relying on triggers because that means we need to commit 
        # inside every loop
        # 

        logging.debug( '{}.{} ({}) Marking {} {} and {} {} in a relationship'.format( solyear,sol, solday, user1.first_name, user1.family_name, user2.first_name, user2.family_name) )
        user1.state = 'couple'
        user2.state = 'couple'

        r = models.Relationship( 
                id=str(uuid.uuid4()),
                first=user1.id,
                second=user2.id, 
                relationship=models.RelationshipEnum.partner,
                begin_solday=solday)

        # TODO add a callback to randomly break the relationship
        # here (after some random time) or handle it in the main loop ???

        # TODO similar vein - do we handle children here or in main loop ???

        session.add(r)

    session.commit()


##
# break up a family (while partners are alive)
# clearing up a family where one member dies is handled
# in the database layer (models/triggers.py)
def breakup( solday, solyear, sol ):
    pass
