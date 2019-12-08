##
# Original Author: Richard Offer
#
# SQLite functions in Python

import logging

import censere.models

##
# This implements the social policy on whether two people
# are "allowed" to become partners.
# The "legal" stuff (minimum ages, compatible orientations) is
# implemented in the SQL in make(), this handles
# the "softer" policies i.e. closeness of blood relations
# which small communities are more likely to accept than
# a planet sized population with lots of eligible partners
# For example - ex-mother-in-law is typically illegal in
# in Western society - but there is no genetic overlap. 
#
# Possible future policies to be considered
#  * there are insufficient family quarters -> no new families
#  * familes can be extended (more than 2 people) - this would require code changes in families.make()
#  * social policy changes means that only hetrosexual couples are allowed.
#
# Will need a mechanism to change policy over time
def family_policy( id_1, id_2):

    allowed = False

    try:

        relatives_1 = set()
        relatives_2 = set()

        # TODO - make the "relationship limit" configurable
        common_ancestor = censere.models.RelationshipEnum.great_great_great_grandparent
        for r1 in censere.models.Relationship.select(censere.models.Relationship.second).where( 
                ( censere.models.Relationship.first == id_1 ) &
                ( censere.models.Relationship.relationship <= common_ancestor ) 
            ).tuples():
            relatives_1.add( str(r1[0]) )

        for r2 in censere.models.Relationship.select(censere.models.Relationship.second).where( 
                ( censere.models.Relationship.first == id_2 ) &
                ( censere.models.Relationship.relationship <= common_ancestor ) 
            ).tuples():
            relatives_2.add( str(r2[0]) )

        # This blocks siblings - all ancestors are the same
        if relatives_1 == relatives_2:
            allowed = False

        # this should block any overlap between the two people
        if len(relatives_1 & relatives_2) == 0:
            allowed = True

    except Exception as e:

        logging.log( logging.ERROR, 'Caught exception %s', str(e) )

    return allowed


def register_all( db ):

    db.register_function( family_policy, "app_family_policy", num_params=2 )

