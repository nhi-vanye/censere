
import logging
import uuid

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
        # special case of astronaut saved
        # add a dummy relationship of their offworld parents

        if instance.birth_location == "earth":

            s1 = Relationship()

            s1.relationship_id=str(uuid.uuid4())
            s1.first = instance.colonist_id
            s1.second = instance.biological_father
            s1.relationship = RelationshipEnum.parent
            s1.begin_solday = thisApp.solday

            s1.save()

            s2 = Relationship()

            s2.relationship_id=str(uuid.uuid4())
            s2.first = instance.colonist_id
            s2.second = instance.biological_mother
            s2.relationship = RelationshipEnum.parent
            s2.begin_solday = thisApp.solday

            s2.save()

        return

    for i in instance._dirty_field_cache:
        
        if i.name == "death_solday":

            logging.debug( "%d.%d Updated death_solday for %s %s (%d)", *UTILS.from_soldays( thisApp.solday ), instance.first_name, instance.family_name, instance.colonist_id )

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

                logging.info( "%d.%d Relationship %s ended. Death of %s %s",
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

    if instance.relationship == RelationshipEnum.parent:

        # new parent child relationship created
        # so add the parent's relationships onto this as well
        # while incrementing the relationship value
        if created:

            # instance.second is one of the biological parents of instance.first
            # so look at reltionships that are on that parent
            for row in Relationship.select().where( 
                ( Relationship.first == instance.second ) &
                # not a partner relationship
                ( Relationship.relationship > 0 ) ) : 

                r = Relationship()

                r.relationship_id=str(uuid.uuid4())
                r.first = instance.first
                r.second = row.second

                # increase the relationship level
                r.relationship = row.relationship + 1

                r.begin_solday = thisApp.solday

                r.save()

            return

    if instance.relationship == RelationshipEnum.partner:
        if created:

            ( 
                Colonist.update( 
                    { Colonist.state: 'couple'} 
                ).where( 
                    ( Colonist.colonist_id == instance.first ) |
                    ( Colonist.colonist_id == instance.second ) 
                ).execute()
            )

            logging.log( logging.INFO, '%d.%d Created new family %s', *UTILS.from_soldays( thisApp.solday ), instance.relationship_id )
            logging.log( thisApp.DETAILS, '%d.%d Created new family between %s and %s', *UTILS.from_soldays( thisApp.solday ), instance.first, instance.second )

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


