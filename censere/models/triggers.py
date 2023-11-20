
import logging

import pprint

import peewee
import playhouse.signals 

from censere.config import thisApp
import censere.utils as UTILS
import censere.utils.random as RANDOM
import censere.events as EVENTS

from .settler import Settler as Settler
from .settler import LocationEnum as LocationEnum
from .relationship import Relationship as Relationship
from .relationship import RelationshipEnum as RelationshipEnum
from .resources import CommodityResevoir as CommodityResevoir
from .resources import CommodityResevoirCapacity as CommodityResevoirCapacity
from .resources import CommodityUsage as CommodityUsage

LOGGER = logging.getLogger("c.m.triggers")
DEVLOG = logging.getLogger("d.devel")

##
# Be careful here between a class update (Settler.update().where() and
# calling the instance.save() method.
#
# Class methods do NOT trigger pre- and post triggers. So know what you want - and document it.


##
# make a local copy of the fields that are being modified
@playhouse.signals.pre_save(sender=Settler)
def settler_pre_save(sender, instance, created):

    if not created:
        instance._dirty_field_cache = instance.dirty_fields

##
#
@playhouse.signals.post_save(sender=Settler)
def settler_post_save(sender, instance, created):

    if created:
        # special case of astronaut saved
        # add a dummy relationship of their offworld parents

        if instance.birth_location == LocationEnum.Earth:

            s1 = Relationship()

            s1.simulation_id=thisApp.simulation

            s1.relationship_id= RANDOM.id()
            s1.first = instance.settler_id
            s1.second = instance.biological_father
            s1.relationship = RelationshipEnum.parent
            s1.begin_solday = thisApp.solday

            s1.save()

            s2 = Relationship()

            s2.simulation_id=thisApp.simulation

            s2.relationship_id= RANDOM.id()
            s2.first = instance.settler_id
            s2.second = instance.biological_mother
            s2.relationship = RelationshipEnum.parent
            s2.begin_solday = thisApp.solday

            s2.save()

        return

    for i in instance._dirty_field_cache:
        
        if i.name == "death_solday":

            LOGGER.debug( "%d.%03d Updated death_solday for %s %s (%s)", *UTILS.from_soldays( thisApp.solday ), instance.first_name, instance.family_name, instance.settler_id )

            # When a person dies only their partner relationship ends
            # We don't remove any child/parent relationship links

            for r in Relationship().select().filter( 
                ( Relationship.relationship == RelationshipEnum.partner ) &
                ( Relationship.end_solday == 0 ) &
                ( 
                    ( Relationship.first == instance.settler_id ) | 
                    ( Relationship.second == instance.settler_id )
                )):

                # in this case we want to treat this as a break up so we can reset
                # the surviving partner to single - so call any triggers...
                r.end_solday = thisApp.solday

                LOGGER.info( "%d.%03d Relationship %s ended. Death of %s %s",
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

                r.simulation_id=thisApp.simulation

                r.relationship_id= RANDOM.id()
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
                Settler.update( 
                    { Settler.state: 'couple'} 
                ).where( 
                    ( Settler.settler_id == instance.first ) |
                    ( Settler.settler_id == instance.second ) 
                ).execute()
            )

            LOGGER.log( logging.INFO, '%d.%03d Created new family %s', *UTILS.from_soldays( thisApp.solday ), instance.relationship_id )
            LOGGER.log( thisApp.DETAIL, '%d.%03d Created new family between %s and %s', *UTILS.from_soldays( thisApp.solday ), instance.first, instance.second )

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
                            Settler.update( 
                                { Settler.state: 'single'} 
                            ).where( 
                                ( ( Settler.settler_id == instance.first ) |
                                ( Settler.settler_id == instance.second ) ) &
                                ( Settler.death_solday == 0 )
                            ).execute()
                        )


###
#
# additional triggers needed
#   update a person's productivity as the age/pregnant/maternity/paternity leave
#   update a person's resource consumption (oxygen etc) as they grow from birth
#   update habitation needs as families change

