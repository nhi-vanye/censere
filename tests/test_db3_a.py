
import pytest
import logging

from censere.config import Generator as thisApp
import censere.models
import censere.actions

thisApp.simulation = "00000000-0000-0000-0000-000000000000"
thisApp.astronaut_age_range = "32,45"
thisApp.solday = 1


class TestCreateUnacceptableFamilies:

    # provide access to logged messages from the library calls
    # This can be used for example to see what is happening in the
    # library code by setting the libray logging to DEBUG
    # i.e. in the test functions add
    #
    #    self._caplog.set_level(logging.DEBUG)
    #
    @pytest.fixture(autouse=True)
    def add_access_to_logging(self, caplog):
        self._caplog = caplog
    

    def test_create_gen1_colonists(self, database):
        database.bind( [ censere.models.Astronaut ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Astronaut ] )
        assert database.table_exists( "colonists" )

        a = censere.models.Astronaut()

        a.initialize( 1, sex='m', config=thisApp )

        # use a well known ID to make it easier to find
        a.colonist_id = "aaaaaaaa-1111-0000-0000-000000000000"
        a.orientation = 'f'

        assert a.save() == 1
        assert censere.models.Colonist.select().where( 
                    ( censere.models.Colonist.simulation == thisApp.simulation ) &
                    ( censere.models.Colonist.colonist_id == "aaaaaaaa-1111-0000-0000-000000000000" )
               ).count() == 1

        b = censere.models.Astronaut()

        b.initialize( 1, sex='f', config=thisApp )
        b.orientation = 'm'

        # use a well known ID to make it easier to find
        b.colonist_id = "aaaaaaaa-2222-0000-0000-000000000000"

        assert b.save() == 1
        assert censere.models.Colonist.select().where( 
                    ( censere.models.Colonist.simulation == thisApp.simulation ) &
                    ( censere.models.Colonist.colonist_id == "aaaaaaaa-2222-0000-0000-000000000000" )
               ).count() == 1


    def test_make_gen1_family(self, database):
        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Relationship ] )
        assert database.table_exists( "relationships" )

        censere.actions.make_families( )

        assert censere.models.Relationship.select().count() == 1

        assert censere.models.Colonist.select().where( 
                    ( censere.models.Colonist.state == 'couple' )
               ).count() == 2

    def test_make_gen2_children(self, database):
        database.bind( [ censere.models.Colonist, censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )

        # id is a hidden field - normally prefer
        # relationship_id but that is random
        family = censere.models.Relationship.get( censere.models.Relationship.id == 1 ) 

        assert family.relationship == censere.models.RelationshipEnum.partner

        first = censere.models.Colonist.get( censere.models.Colonist.colonist_id == str(family.first) )
        second = censere.models.Colonist.get( censere.models.Colonist.colonist_id == str(family.second) )

        mother = None
        father = None

        assert first.sex != second.sex

        if first.sex == 'm':
            father = first
            mother = second
        else:
            mother = first
            father = second

        kwargs = { "biological_mother" : mother.colonist_id, "biological_father": father.colonist_id }

        son1 = censere.models.Martian()

        son1.initialize( 1, config=thisApp )

        # use a well known ID to make it easier to find
        son1.colonist_id = "aaaaaaaa-3333-0000-0000-000000000000"

        son1.biological_father = str(father.colonist_id)
        son1.biological_mother = str(mother.colonist_id)

        son1.family_name = father.family_name

        assert son1.save() == 1

        r = censere.models.Relationship()

        r.relationship_id = "aaaaaaaa-2222-0000-0000-000000000000"
        r.first = father.colonist_id
        r.second = son1.colonist_id
        r.relationship = censere.models.RelationshipEnum.child
        r.begin_solday = 1

        assert r.save() == 1

        son2 = censere.models.Martian()

        son2.initialize( 1, config=thisApp )

        # use a well known ID to make it easier to find
        son2.colonist_id = "aaaaaaaa-4444-0000-0000-000000000000"

        son2.biological_father = str(father.colonist_id)
        son2.biological_mother = str(mother.colonist_id)

        son2.family_name = father.family_name

        assert son2.save() == 1

        r = censere.models.Relationship()

        r.relationship_id = "aaaaaaaa-3333-0000-0000-000000000000"
        r.first = father.colonist_id
        r.second = son2.colonist_id
        r.relationship = censere.models.RelationshipEnum.child
        r.begin_solday = 1

        assert r.save() == 1

        daughter1 = censere.models.Martian()

        daughter1.initialize( 1, config=thisApp )

        # use a well known ID to make it easier to find
        daughter1.colonist_id = "aaaaaaaa-5555-0000-0000-000000000000"

        daughter1.biological_father = str(father.colonist_id)
        daughter1.biological_mother = str(mother.colonist_id)

        daughter1.family_name = father.family_name

        assert daughter1.save() == 1

        r = censere.models.Relationship()

        r.relationship_id = "aaaaaaaa-4444-0000-0000-000000000000"
        r.first = father.colonist_id
        r.second = daughter1.colonist_id
        r.relationship = censere.models.RelationshipEnum.child
        r.begin_solday = 1

        assert r.save() == 1

        daughter2 = censere.models.Martian()

        daughter2.initialize( 1, config=thisApp )

        # use a well known ID to make it easier to find
        daughter2.colonist_id = "aaaaaaaa-6666-0000-0000-000000000000"

        daughter2.biological_father = str(father.colonist_id)
        daughter2.biological_mother = str(mother.colonist_id)

        daughter2.family_name = father.family_name

        assert daughter2.save() == 1

        r = censere.models.Relationship()

        r.relationship_id = "aaaaaaaa-5555-0000-0000-000000000000"
        r.first = father.colonist_id
        r.second = daughter2.colonist_id
        r.relationship = censere.models.RelationshipEnum.child
        r.begin_solday = 1

        assert r.save() == 1

    @pytest.mark.xfail
    def test_dont_make_family_from_siblings(self, database):
        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )

        # need to move time on so gen1 children are older than 18

        thisApp.solday = int(20 * 365.25 * 1.02749125)

        #self._caplog.set_level(logging.DEBUG)
        censere.actions.make_families( )

        # all gen2 people have the same parents so we
        # should not have created any more families
        assert censere.models.Relationship.select().where( 
                censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner
            ).count() == 1

    def test_dont_make_family_from_cousins(self, database):
        pytest.skip("Not implemented yet")


    # relationships between man and ex mother-in law (as example)
    # are typically not socially acceptable even though
    # there is no blood relationship
    def test_dont_make_family_between_inlaws(self, database):
        pytest.skip("Not implemented yet")

    # decide if we accept 2nd cousins as partners
    def test_make_family_from_second_cousins(self, database):
        pytest.skip("Not implemented yet")

