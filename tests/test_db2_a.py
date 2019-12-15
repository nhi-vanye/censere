
import pytest
import logging

from censere.config import Generator as thisApp
import censere.models
import censere.actions

thisApp.simulation = "00000000-0000-0000-0000-000000000000"
thisApp.astronaut_age_range = "32,45"
thisApp.solday = 1
thisApp.orientation = "90,6,4"
thisApp.astronaut_gender_ratio = "50,50"
thisApp.astronaut_life_expectancy = "72,7"
thisApp.martian_gender_ratio = "50,50"
thisApp.martian_life_expectancy = "72,7"
thisApp.first_child_delay = "400,700"
thisApp.gap_between_siblings = "380,1000"


class TestCreatingFamilies:

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

    def test_create_two_straight_male_astronauts(self, database):
        database.bind( [ censere.models.Astronaut ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        # triggers on settlers table now require relationships table to be created
        database.create_tables( [ censere.models.Astronaut, censere.models.Relationship ] )
        assert database.table_exists( "settlers" )

        a = censere.models.Astronaut()

        a.initialize( 1, sex='m', config=thisApp )

        # use a well known ID to make it easier to find
        a.settler_id = "aaaaaaaa-1111-0000-0000-000000000000"
        a.orientation = 'f'

        assert a.save() == 1
        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.simulation == thisApp.simulation ) &
                    ( censere.models.Settler.settler_id == "aaaaaaaa-1111-0000-0000-000000000000" )
               ).count() == 1

        b = censere.models.Astronaut()

        b.initialize( 1, sex='m', config=thisApp )
        b.orientation = 'f'

        # use a well known ID to make it easier to find
        b.settler_id = "aaaaaaaa-2222-0000-0000-000000000000"

        assert b.save() == 1
        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.simulation == thisApp.simulation ) &
                    ( censere.models.Settler.settler_id == "aaaaaaaa-2222-0000-0000-000000000000" )
               ).count() == 1


    def test_fail_make_one_family(self, database):
        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Relationship ] )
        assert database.table_exists( "relationships" )

        self._caplog.set_level(logging.DEBUG)
        censere.actions.make_families( )

        assert censere.models.Relationship.select().where(censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner).count() == 0

        male1 = censere.models.Settler.get( 
                censere.models.Settler.settler_id == "aaaaaaaa-1111-0000-0000-000000000000" ) 

        male2 = censere.models.Settler.get( 
                censere.models.Settler.settler_id == "aaaaaaaa-2222-0000-0000-000000000000" ) 

        assert male1.state == 'single'
        assert male2.state == 'single'

    def test_create_two_straight_female_astronauts(self, database):
        database.bind( [ censere.models.Astronaut ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Astronaut ] )
        assert database.table_exists( "settlers" )

        a = censere.models.Astronaut()

        a.initialize( 1, sex='f', config=thisApp )

        # use a well known ID to make it easier to find
        a.settler_id = "aaaaaaaa-3333-0000-0000-000000000000"
        a.orientation = 'm'

        assert a.save() == 1
        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.simulation == thisApp.simulation ) &
                    ( censere.models.Settler.settler_id == "aaaaaaaa-3333-0000-0000-000000000000" )
               ).count() == 1

        b = censere.models.Astronaut()

        b.initialize( 1, sex='f', config=thisApp )
        b.orientation = 'm'

        # use a well known ID to make it easier to find
        b.settler_id = "aaaaaaaa-4444-0000-0000-000000000000"

        assert b.save() == 1
        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.simulation == thisApp.simulation ) &
                    ( censere.models.Settler.settler_id == "aaaaaaaa-4444-0000-0000-000000000000" )
               ).count() == 1

    def test_make_one_family(self, database):
        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        assert database.table_exists( "relationships" )

        censere.actions.make_families( )

        assert censere.models.Relationship.select().where(censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner).count() == 1

        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.state == 'couple' )
               ).count() == 2

        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.state == 'single' )
               ).count() == 2

    def test_make_second_family(self, database):
        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        assert database.table_exists( "relationships" )


        censere.actions.make_families( )

        assert censere.models.Relationship.select().where(censere.models.Relationship.relationship == censere.models.RelationshipEnum.partner).count() == 2

        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.state == 'couple' )
               ).count() == 4

        assert censere.models.Settler.select().where( 
                    ( censere.models.Settler.state == 'single' )
               ).count() == 0

    def test_settler_pregnant(self, database):
        pytest.skip("Event pipeline not present yet")

    def test_maternity_leave(self, database):
        pytest.skip("Event pipeline not present yet")

    def test_settler_born(self, database):
        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)
        database.connect( reuse_if_open=True )
        assert database.table_exists( "relationships" )

        # id is a hidden field - normally prefer
        # relationship_id but that is random
        family = censere.models.Relationship.get( censere.models.Relationship.id == 10 ) 

        assert family.relationship == censere.models.RelationshipEnum.partner

        first = censere.models.Settler.get( censere.models.Settler.settler_id == str(family.first) )
        second = censere.models.Settler.get( censere.models.Settler.settler_id == str(family.second) )

        mother = None
        father = None

        assert first.sex != second.sex

        if first.sex == 'm':
            father = first.settler_id
            mother = second.settler_id
        else:
            mother = first.settler_id
            father = second.settler_id

        kwargs = { "biological_mother" : mother, "biological_father": father }

        # Call main processing code to create a new born person
        censere.events.callbacks.settler_born( **kwargs )

        assert censere.models.Relationship.select().where(censere.models.Relationship.relationship != censere.models.RelationshipEnum.partner).count() == 14

        child = censere.models.Settler.get( censere.models.Settler.birth_solday == thisApp.solday )

        assert child.biological_father == father
        assert child.biological_mother == mother

        # a child has a mother and father relationship
        assert censere.models.Relationship.select().where( 
                    ( censere.models.Relationship.first == child.settler_id ) & 
                    ( censere.models.Relationship.relationship == censere.models.RelationshipEnum.parent )
               ).count() == 2

    def test_start_paternity_leave(self, database):
        pytest.skip("Event pipeline not present yet")

    def test_end_paternity_leave(self, database):
        pytest.skip("Event pipeline not present yet")

    def test_end_maternity_leave(self, database):
        pytest.skip("Event pipeline not present yet")

    def test_close_database(self, database):

        database.close()

