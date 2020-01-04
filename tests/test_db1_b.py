
import logging
import pytest

from censere.config import Generator as thisApp
import censere.models

thisApp.simulation = "00000000-0000-0000-0000-000000000000"
thisApp.astronaut_age_range = "randint:32,45"
thisApp.orientation = "90,6,4"
thisApp.solday = 1


class TestCreatingAstronaut:

    @pytest.fixture(autouse=True)
    def add_access_to_logging(self, caplog):
        self._caplog = caplog

    def test_create_one_male_astronaut(self, database):
        database.bind( [ censere.models.Astronaut ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        assert database.table_exists( "settlers" )

        row = censere.models.Astronaut()

        self._caplog.set_level(logging.DEBUG)

        row.initialize( 1, sex='m', config=thisApp )

        # use a well known ID to make it easier to find
        row.settler_id = "aaaaaaaa-1111-0000-0000-000000000000"

        assert row.save() == 1
        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.simulation_id == thisApp.simulation ) &
                    ( censere.models.Settler.settler_id == "aaaaaaaa-1111-0000-0000-000000000000" )
               ).count() == 1

    def test_create_one_female_astronaut(self, database):
        database.bind( [ censere.models.Astronaut ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        assert database.table_exists( "settlers" )

        row = censere.models.Astronaut()

        row.initialize( 1, sex='f', config=thisApp )

        # use a well known ID to make it easier to find
        row.settler_id = "aaaaaaaa-2222-0000-0000-000000000000"

        assert row.save() == 1
        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.simulation_id == thisApp.simulation ) &
                    ( censere.models.Settler.settler_id == "aaaaaaaa-2222-0000-0000-000000000000" )
               ).count() == 1


    def test_create_one_relationship(self, database):
        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        assert database.table_exists( "relationships" )

        male = censere.models.Settler.get( 
                censere.models.Settler.settler_id == "aaaaaaaa-1111-0000-0000-000000000000" ) 
        female = censere.models.Settler.get( 
                censere.models.Settler.settler_id == "aaaaaaaa-2222-0000-0000-000000000000" )

        assert str(male.settler_id) == "aaaaaaaa-1111-0000-0000-000000000000"
        assert str(female.settler_id) == "aaaaaaaa-2222-0000-0000-000000000000"


        r = censere.models.Relationship()

        r.simulation_id = thisApp.simulation
        r.relationship_id = "aaaaaaaa-0000-0000-0000-000000000000"
        r.first = male.settler_id
        r.second = female.settler_id
        r.relationship = censere.models.RelationshipEnum.partner
        r.begin_solday = 1

        assert r.save() == 1
        assert censere.models.Relationship.select().where( 
                ( censere.models.Relationship.relationship_id == "aaaaaaaa-0000-0000-0000-000000000000" )
                ).count() == 1

    def test_create_one_martian(self, database):
        database.bind( [ censere.models.Martian ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        assert database.table_exists( "settlers" )

        row = censere.models.Martian()

        row.initialize( 1, config=thisApp )

        # use a well known ID to make it easier to find
        row.settler_id = "aaaaaaaa-3333-0000-0000-000000000000"

        male = censere.models.Settler.get( 
                censere.models.Settler.settler_id == "aaaaaaaa-1111-0000-0000-000000000000" ) 
        female = censere.models.Settler.get( 
                censere.models.Settler.settler_id == "aaaaaaaa-2222-0000-0000-000000000000" )

        row.biological_father = str(male.settler_id)
        row.biological_mother = str(female.settler_id)

        row.family_name = male.family_name

        assert row.save() == 1

        assert censere.models.Martian.select().where( 
                    ( censere.models.Martian.simulation_id == thisApp.simulation ) &
                    ( censere.models.Martian.settler_id == "aaaaaaaa-3333-0000-0000-000000000000" )
               ).count() == 1

        child = censere.models.Settler.get( 
                censere.models.Settler.settler_id == "aaaaaaaa-3333-0000-0000-000000000000" ) 

        assert str(child.biological_father) == "aaaaaaaa-1111-0000-0000-000000000000"
        assert str(child.biological_mother) == "aaaaaaaa-2222-0000-0000-000000000000"


        assert censere.models.Settler.select().count() == 3

        # finished with this in-memory database
        # the next test case will need to create a new one`
        database.close()

