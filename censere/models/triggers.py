
import logging

import playhouse.signals 

from censere.config import Generator as thisApp
import censere.utils as UTILS

from .colonist import Colonist as Colonist
from .relationship import Relationship as Relationship
from .relationship import RelationshipEnum as RelationshipEnum

##
# Be careful here between a class update (Colonist.update().where() and
# calling the instance.save() method.
#
# Class methods do NOT trigger pre- and post triggers. So know what you want - and document it.


##
# make a local copy of the fields that are being modified
@playhouse.signals.pre_save(sender=Colonist)
def colonist_pre_save(sender, instance, created):

    if not created:
        instance._dirty_field_cache = instance.dirty_fields

##
# When a person dies we need to close out any PARTNER relationships
# they were in.
#
@playhouse.signals.post_save(sender=Colonist)
def colonist_post_save(sender, instance, created):

    if created:
        return

    for i in instance._dirty_field_cache:
        
        if i.name == "death_solday":

            logging.debug( "%.% Updated death_solday for % % (%)", *UTILS.from_soldays( thisApp.solday ), instance.first_name, instance.family_name, instance.colonist_id )

            # When a person dies only their partner relationship ends
            # We don't remove any child/parent relationship links

            for r in Relationship().select().filter( 
                ( Relationship.relationship == RelationshipEnum.partner ) &
                ( Relationship.end_solday == 0 ) &
                ( 
                    ( Relationship.first == instance.colonist_id ) | 
                    ( Relationship.second == instance.colonist_id )
                )):

                # in this case we want to treat this as a break up so we can reset
                # the surviving partner to single - so call any triggers...
                r.end_solday = thisApp.solday

                logging.info( "%.% Relationship % ended. Death of % %",
                    *UTILS.from_soldays( thisApp.solday ),
                    r.relationship_id,
                    instance.first_name,
                    instance.family_name)

                r.save()

##
# make a local copy of the fields that are being modified
@playhouse.signals.pre_save(sender=Relationship)
def relationship_pre_save(sender, instance, created):

    if not created:
        instance._dirty_field_cache = instance.dirty_fields

## 
#
@playhouse.signals.post_save(sender=Relationship)
def relationship_post_save(sender, instance, created):

    if instance.relationship != RelationshipEnum.partner:
        return

    if created:

        ( 
            Colonist.update( 
                { Colonist.state: 'couple'} 
            ).where( 
                ( Colonist.colonist_id == instance.first ) |
                ( Colonist.colonist_id == instance.second ) 
            ).execute()
        )

        logging.info('%.% Created new family %', *UTILS.from_soldays( thisApp.solday ), instance.relationship_id )
        logging.log( thisApp.DETAILS, '%.% Created new family between % and %', *UTILS.from_soldays( thisApp.solday ), instance.relationship_id, instance.first, instance.second )

    else:

        # iterate over dirty fields

        for i in instance._dirty_field_cache:
        
            if i.name == "end_solday":

                # relationship has ended
                if instance.end_solday != 0:

                    ## By making this a class update it wont initiate any
                    # triggers (pre_save or post_save)
                    # update each of the partners to make them single again
                    # if they are not dead.
                    ( 
                        Colonist.update( 
                            { Colonist.state: 'single'} 
                        ).where( 
                            ( ( Colonist.colonist_id == instance.first ) |
                            ( Colonist.colonist_id == instance.second ) ) &
                            ( Colonist.death_solday == 0 )
                        ).execute()
                    )


###
#
# additional triggers needed
#   update a person's productivity as the age/pregnant/maternity/paternity leave
#   update a person's resource consumption (oxygen etc) as they grow from birth
#   update habitation needs as families change


