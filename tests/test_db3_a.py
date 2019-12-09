
import pytest
import logging
import uuid

from censere.config import Generator as thisApp
import censere.models
import censere.actions

thisApp.simulation = "00000000-0000-0000-0000-000000000000"
thisApp.astronaut_age_range = "32,45"
thisApp.solday = 1
thisApp.orientation = "90,6,4"
thisApp.astronaut_gender_ratio = "50,50"
thisApp.martian_gender_ratio = "50,50"
thisApp.initial_child_delay = "400,700"
thisApp.gap_between_children = "380,1000"


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

    ##
    # helper to create a person and connected relationships
    def make_martian(self, sex, settler_id, orientation, father_id, mother_id, family_name ):

        p = censere.models.Martian()

        p.initialize( 1, sex=sex, config=thisApp )
        p.orientation = orientation

        # use a well known ID to make it easier to find
        p.settler_id = settler_id

        p.biological_father = str(father_id)
        p.biological_mother = str(mother_id)

        p.family_name = family_name

        assert p.save() == 1

        r1 = censere.models.Relationship()

        r1.relationship_id = settler_id.replace('a', 'A')
        r1.first = settler_id
        r1.second = father_id
        r1.relationship = censere.models.RelationshipEnum.parent
        r1.begin_solday = thisApp.solday

        assert r1.save() == 1

        r2 = censere.models.Relationship()

        r2.relationship_id = settler_id.replace('a', 'B')
        r2.first = settler_id
        r2.second = mother_id
        r2.relationship = censere.models.RelationshipEnum.parent
        r2.begin_solday = 1

        assert r2.save() == 1

    def make_astronaut(self, sex, settler_id, orientation, father_id, mother_id ):

        p = censere.models.Astronaut()

        p.initialize( 1, sex=sex, config=thisApp )
        p.orientation = orientation

        # use a well known ID to make it easier to find
        p.settler_id = settler_id

        p.biological_father = str(father_id)
        p.biological_mother = str(mother_id)

        assert p.save() == 1

        r1 = censere.models.Relationship()

        r1.relationship_id = settler_id.replace('a', 'A')
        r1.first = settler_id
        r1.second = father_id
        r1.relationship = censere.models.RelationshipEnum.parent
        r1.begin_solday = thisApp.solday

        assert r1.save() == 1

        r2 = censere.models.Relationship()

        r2.relationship_id = settler_id.replace('a', 'B')
        r2.first = settler_id
        r2.second = mother_id
        r2.relationship = censere.models.RelationshipEnum.parent
        r2.begin_solday = 1

        assert r2.save() == 1
  

    def test_create_gen1_settlers(self, database):
        database.bind( [ censere.models.Astronaut ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Astronaut, censere.models.Relationship ] )
        assert database.table_exists( "settlers" )

        self.make_astronaut( 'm', "aaaaaaaa-1111-0000-0000-000000000000", 'f', str(uuid.uuid4()), str(uuid.uuid4()))

        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.simulation == thisApp.simulation ) &
                    ( censere.models.Settler.settler_id == "aaaaaaaa-1111-0000-0000-000000000000" )
               ).count() == 1

        self.make_astronaut( 'f', "aaaaaaaa-2222-0000-0000-000000000000", 'm', str(uuid.uuid4()), str(uuid.uuid4()))

        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.simulation == thisApp.simulation ) &
                    ( censere.models.Settler.settler_id == "aaaaaaaa-2222-0000-0000-000000000000" )
               ).count() == 1


    def test_make_gen1_family(self, database):
        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Relationship ] )
        assert database.table_exists( "relationships" )

        assert censere.models.Relationship.select().where(censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner).count() == 0

        censere.actions.make_families( )

        assert censere.models.Relationship.select().where(censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner).count() == 1

        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.state == 'couple' )
               ).count() == 2

    def test_make_gen2_children(self, database):
        database.bind( [ censere.models.Settler, censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )

        family = censere.models.Relationship.get( 
            ( ( censere.models.Relationship.first == "aaaaaaaa-1111-0000-0000-000000000000"  ) |
              ( censere.models.Relationship.second == "aaaaaaaa-1111-0000-0000-000000000000"  ) ) & 
            ( ( censere.models.Relationship.first == "aaaaaaaa-2222-0000-0000-000000000000"  ) |
              ( censere.models.Relationship.second == "aaaaaaaa-2222-0000-0000-000000000000"  ) ) )

        assert family.relationship == censere.models.RelationshipEnum.partner

        first = censere.models.Settler.get( censere.models.Settler.settler_id == str(family.first) )
        second = censere.models.Settler.get( censere.models.Settler.settler_id == str(family.second) )

        mother = None
        father = None

        assert first.sex != second.sex

        if first.sex == 'm':
            father = first
            mother = second
        else:
            mother = first
            father = second

        self.make_martian( 'm', "aaaaaaaa-3333-0000-0000-000000000000", 'f', father.settler_id, mother.settler_id, father.family_name )

        self.make_martian( 'm', "aaaaaaaa-4444-0000-0000-000000000000", 'f', father.settler_id, mother.settler_id, father.family_name )


        self.make_martian( 'f', "aaaaaaaa-5555-0000-0000-000000000000", 'm', father.settler_id, mother.settler_id, father.family_name )

        self.make_martian( 'f', "aaaaaaaa-6666-0000-0000-000000000000", 'm', father.settler_id, mother.settler_id, father.family_name )

    def test_dont_make_family_from_siblings(self, database):
        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )

        # need to move time on so gen1 children are older than 18

        thisApp.solday = int(20 * 365.25 * 1.02749125)

        assert censere.models.Relationship.select().where( 
                censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner
            ).count() == 1

        #self._caplog.set_level(logging.DEBUG)
        censere.actions.make_families( )

        # all gen2 people have the same parents so we
        # should not have created any more families
        assert censere.models.Relationship.select().where( 
                censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner
            ).count() == 1

    def test_make_gen3_children(self, database):
        database.bind( [ censere.models.Settler, censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )

        father_1 = censere.models.Settler.get( censere.models.Settler.settler_id == "aaaaaaaa-3333-0000-0000-000000000000" )

        self.make_martian( 'm', "aaaaaaaa-8888-0000-0000-000000000000", 'f', "aaaaaaaa-3333-0000-0000-000000000000",  "aaaaaaaa-5555-0000-0000-000000000000", father_1.family_name )


        father_2 = censere.models.Settler.get( censere.models.Settler.settler_id == "aaaaaaaa-3333-0000-0000-000000000000" )
        self.make_martian( 'm', "aaaaaaaa-9999-0000-0000-000000000000", 'f', "aaaaaaaa-4444-0000-0000-000000000000",  "aaaaaaaa-6666-0000-0000-000000000000", father_2.family_name )


    def test_dont_make_family_from_cousins(self, database):
        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )

        # need to move time on so gen3 children are older than 18

        thisApp.solday = int(40 * 365.25 * 1.02749125)

        assert censere.models.Relationship.select().where( 
                censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner
            ).count() == 1

        #self._caplog.set_level(logging.DEBUG)
        censere.actions.make_families( )

        # all gen3 people have the same grandparents so we
        # should not have created any more families
        assert censere.models.Relationship.select().where( 
                censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner
            ).count() == 1



    # relationships between man and ex mother-in law (as example)
    # are typically not socially acceptable even though
    # there is no blood relationship
    def test_dont_make_family_between_inlaws(self, database):
        pytest.skip("Not implemented yet")

    # decide if we accept 2nd cousins as partners
    def test_make_family_from_second_cousins(self, database):
        pytest.skip("Not implemented yet")


    def test_close(self, database):
        database.close()

