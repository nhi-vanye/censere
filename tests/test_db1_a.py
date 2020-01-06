import pytest

import censere.models

class TestCreateTables:
    def test_create_event_table(self, database):

        database.bind( [ censere.models.Event ], bind_refs=False, bind_backrefs=False)

        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Event ] )
        assert database.table_exists( "events" )

    def test_create_settler_table(self, database):

        database.bind( [ censere.models.Settler ], bind_refs=False, bind_backrefs=False)

        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Settler ] )
        assert database.table_exists( "settlers" )

    def test_create_relationship_table(self, database):

        database.bind( [ censere.models.Relationship ], bind_refs=False, bind_backrefs=False)

        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Relationship ] )
        assert database.table_exists( "relationships" )

    def test_create_simulation_table(self, database):

        database.bind( [ censere.models.Simulation ], bind_refs=False, bind_backrefs=False)

        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Simulation ] )
        assert database.table_exists( "simulations" )

    def test_create_summary_table(self, database):

        database.bind( [ censere.models.Summary ], bind_refs=False, bind_backrefs=False)

        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Summary ] )
        assert database.table_exists( "summary" )

    def test_create_demographics_table(self, database):

        database.bind( [ censere.models.Demographic ], bind_refs=False, bind_backrefs=False)

        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Demographic ] )
        assert database.table_exists( "demographics" )

    def test_create_population_table(self, database):

        database.bind( [ censere.models.Population ], bind_refs=False, bind_backrefs=False)

        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Population ] )
 
        assert database.table_exists( "populations" )

    def test_table_count(self, database):

        database.bind( [ censere.models.Summary ], bind_refs=False, bind_backrefs=False)

        database.connect( reuse_if_open=True )
        assert len( database.get_tables( ) ) == 7
        # These need to be in alphabetical order
        assert database.get_tables( ) == [  'demographics', 'events', 'populations', 'relationships', 'settlers', 'simulations', 'summary' ] 


