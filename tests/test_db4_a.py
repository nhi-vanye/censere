
import pytest
import logging
import uuid

from censere.config import Generator as thisApp
import censere.models
import censere.actions

thisApp.simulation = "00000000-0000-0000-0000-000000000000"
thisApp.astronaut_age_range = "randint:32,45"
#thisApp.astronaut_age_range = "half:25,5"
thisApp.solday = 1
thisApp.orientation = "90,6,4"
thisApp.astronaut_gender_ratio = "50,50"
thisApp.astronaut_life_expectancy = "cdc:"
thisApp.martian_gender_ratio = "50,50"
thisApp.martian_life_expectancy = "cdc"
thisApp.first_child_delay = "randint:300,500"
thisApp.sols_between_siblings = "randint:300,1000"
thisApp.fraction_relationships_having_children = 0.9
thisApp.partner_max_age_difference = 20


class TestBenchmarkMakeFamilies:

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

    def test_create_events(self, database):
        database.bind( [ censere.models.Event ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Event ] )
        assert database.table_exists( "events" )

    def make_astronaut(self, father_id, mother_id ):

        p = censere.models.Astronaut()

        p.initialize( thisApp.solday )
        p.settler_id = uuid.uuid4()

        assert p.save() == 1

        r1 = censere.models.Relationship()

        r1.simulation_id = thisApp.simulation
        r1.relationship_id = uuid.uuid4()
        r1.first = p.settler_id
        r1.second = father_id
        r1.relationship = censere.models.RelationshipEnum.parent
        r1.begin_solday = thisApp.solday

        assert r1.save() == 1

        r2 = censere.models.Relationship()

        r2.simulation_id = thisApp.simulation
        r2.relationship_id = uuid.uuid4()
        r2.first = p.settler_id
        r2.second = mother_id
        r2.relationship = censere.models.RelationshipEnum.parent
        r2.begin_solday = 1

        assert r2.save() == 1
  

    def test_make_10_astronauts(self, database):
        database.bind( [ censere.models.Astronaut, censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Astronaut, censere.models.Relationship ] )
        assert database.table_exists( "settlers" )


        for i in range(10):
            self.make_astronaut( str(uuid.uuid4()), str(uuid.uuid4()))

        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.simulation_id == thisApp.simulation )
               ).count() == 10

    def test_make_family_with_10_settlers(self, database, benchmark):
        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Relationship ] )
        assert database.table_exists( "relationships" )

        assert censere.models.Relationship.select().where(censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner).count() == 0

        # lock benchmark to only call make_families() once
        # While not good for benchmarking absolute performance, calling it
        # has side effects that mean we can't use assets to check that we got 1 row created.
        benchmark.pedantic(censere.actions.make_families, rounds=1, iterations=1)

        assert censere.models.Relationship.select().where(censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner).count() == 1

    def test_make_90_astronauts(self, database):
        database.bind( [ censere.models.Astronaut, censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Astronaut, censere.models.Relationship ] )
        assert database.table_exists( "settlers" )


        for i in range(90):
            self.make_astronaut( str(uuid.uuid4()), str(uuid.uuid4()))

        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.simulation_id == thisApp.simulation )
               ).count() == 100

    def test_make_family_with_100_settlers(self, database, benchmark):
        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Relationship ] )
        assert database.table_exists( "relationships" )

        assert censere.models.Relationship.select().where(censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner).count() == 1

        benchmark.pedantic(censere.actions.make_families, rounds=1, iterations=1)

        assert censere.models.Relationship.select().where(censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner).count() == 2

    def test_make_150_astronauts(self, database):
        database.bind( [ censere.models.Astronaut, censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Astronaut, censere.models.Relationship ] )
        assert database.table_exists( "settlers" )


        for i in range(150):
            self.make_astronaut( str(uuid.uuid4()), str(uuid.uuid4()))

        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.simulation_id == thisApp.simulation )
               ).count() == 250

    def test_make_family_with_250_settlers(self, database, benchmark):
        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Relationship ] )
        assert database.table_exists( "relationships" )

        assert censere.models.Relationship.select().where(censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner).count() == 2
        benchmark.pedantic(censere.actions.make_families, rounds=1, iterations=1)
        assert censere.models.Relationship.select().where(censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner).count() == 3

