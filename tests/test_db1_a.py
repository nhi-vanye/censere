import pytest

import censere.models

class TestCreateTables:
    def test_create_colonist_table(self, database):

        database.bind( [ censere.models.Colonist ], bind_refs=False, bind_backrefs=False)

        database.connect( reuse_if_open=True )
        database.create_tables( [ censere.models.Colonist ] )
        assert database.table_exists( "colonists" )

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

    def test_table_count(self, database):

        database.bind( [ censere.models.Summary ], bind_refs=False, bind_backrefs=False)

        database.connect( reuse_if_open=True )
        assert len( database.get_tables( ) ) == 4
        assert database.get_tables( ) == [ 'colonists', 'relationships', 'simulations', 'summary' ] 


