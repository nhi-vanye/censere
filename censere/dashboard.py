
import argparse
import logging
import sys

import sqlite3
import pandas as pd

import webbrowser
import json

import dash
import dash_core_components as DCC
import dash_html_components as HTML
import dash_table as TABLE

from censere.config import Viewer as thisApp
from censere.config import ViewerOptions as OPTIONS


def initialize_arguments_parser( argv ):

    parser = argparse.ArgumentParser(
        fromfile_prefix_chars='@',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Mars Censere Viewer""",
        epilog="""
Arguments that start with '@' will be considered filenames that
specify arguments to the program - ONE ARGUMENT PER LINE.

The Database should be on a local disk - not in Dropbox etc.
""")

    OPTIONS().register( parser )

    args = parser.parse_args( namespace = thisApp )

    log_msg_format = '%(asctime)s %(levelname)5s %(message)s'

    logging.addLevelName(thisApp.NOTICE, "NOTICE")

    log_level = thisApp.NOTICE

    # shortcut
    if thisApp.debug:

        log_msg_format='%(asctime)s.%(msecs)03d %(levelname)5s %(filename)s#%(lineno)-3d %(message)s'

        log_level = logging.DEBUG    

    else:

        log_level = thisApp.log_level

    logging.basicConfig(level=log_level, format=log_msg_format, datefmt='%Y-%m-%dT%H:%M:%S')


def main( argv ):

    cnx = sqlite3.connect( thisApp.database )

    app = dash.Dash(__name__)

    population = {}

    population['query'] = """
SELECT sum.*,
    CASE 
        WHEN sim.notes = '' THEN sim.simulation_id 
        ELSE sim.notes || ' ' || sim.simulation_id
    END as unique_notes,
    CASE 
        WHEN sim.notes = '' THEN sim.simulation_id 
        ELSE sim.notes 
    END as notes
FROM summary sum, simulations sim
WHERE sum.simulation_id = sim.simulation_id AND sum.solday % 668 = 28
"""
    population['df'] = pd.read_sql_query( population['query'], cnx )
    population['min_range'] = 0
    population['max_range'] = int( population['df']['solday'].max() / 668.0 )


    pop_pyramid = {}

    pop_pyramid['query'] = """
SELECT pop.*,
    CASE 
        WHEN sim.notes = '' THEN sim.simulation_id 
        ELSE sim.notes || ' ' || sim.simulation_id
    END as notes
FROM populations pop, simulations sim
WHERE pop.simulation_id = sim.simulation_id"""

    pop_pyramid['df'] = pd.read_sql_query( pop_pyramid['query'], cnx )

    pop_pyramid['min_range'] = 0
    pop_pyramid['max_range'] = int( pop_pyramid['df']['solday'].max() / 668.0 )

    pop_dynamics = {}

    pop_dynamics['query'] = """
SELECT demo.*,
    CASE 
        WHEN sim.notes = '' THEN sim.simulation_id 
        ELSE sim.notes || ' ' || sim.simulation_id
    END as notes
FROM demographics demo, simulations sim
WHERE demo.simulation_id = sim.simulation_id"""

    pop_dynamics['df'] = pd.read_sql_query( pop_dynamics['query'], cnx )

    pop_dynamics['min_range'] = 0
    pop_dynamics['max_range'] = int( pop_dynamics['df']['solday'].max() / 668.0 )

    simulations = {}

    # Dropdown requires struct of { "label" : STR, "value" : VAL }
    simulations['query'] = """
SELECT 
    sim.simulation_id as value,
    CASE 
        WHEN sim.notes = '' THEN sim.simulation_id 
        ELSE sim.notes || ' (' || sim.simulation_id || ')'
    END as label
FROM
    simulations sim
"""
    simulations['df'] = pd.read_sql_query( simulations['query'], cnx )
 
    simulations_list = simulations['df'].to_dict('records')

    sims = {}
    sims['query'] = """
SELECT 
    *
FROM
    simulations sim
"""
    sims['df'] = pd.read_sql_query( sims['query'], cnx )
 
    app.layout = HTML.Div(children=[
        HTML.H1(children='Mars Censere')

        , HTML.H4('Overall Population')
        , DCC.Graph( id='population')
        , HTML.P("")
        , TABLE.DataTable(
            id='table',
            columns=[
                { "name": "simulation_id", "id" : "simulation_id" },
                { "name": "notes", "id" : "notes" },
                { "name": "final_soldays", "id" : "final_soldays" },
                { "name": "final_population", "id" : "final_population" },
                { "name": "random_seed", "id" : "random_seed" },
            ],
            data=sims['df'].to_dict('records')
        )
        , HTML.H4('Population Demographics')
        , HTML.Div([
            HTML.Div([
                HTML.Div([
                    HTML.Label("Year Selector", htmlFor="pyramid-slider")
                    , DCC.Slider(
                            id='pyramid-slider',
                            min=pop_pyramid['min_range'],
                            max=pop_pyramid['max_range'],
                            value=0,
                            step=1
                        )
                    #, HTML.P(id="pyramid-label")
                    , HTML.Label("Filter", htmlFor="sim-selector")
                    , DCC.Dropdown(
                            id='sim-selector',
                            options=simulations_list
                    )
                ]
                ,className="one-half column"
            )
            ])
            , HTML.Div([
                HTML.P(id="pyramid-heading")
                , DCC.Graph( id='pyramid')
                ]
                , className="one-half column"
            )
        ])
        , HTML.Div([
            HTML.Div([
                HTML.H4('Birth & Death Rates')
                , DCC.Graph( id='rates')
                ]
                ,className="one-third column"
            )
            , HTML.Div([
                HTML.H4("Realtionships")
                , DCC.Graph( id='partners')
            ]
            ,className="one-third column"
            )
            , HTML.Div([
                HTML.H4("Settler Status")
                , DCC.Graph( id='status' )
            ]
            ,className="one-third column"
            )        
        ])
        , HTML.Div(id='simulation-id', style={'display': 'none'})
        , HTML.Div([
            HTML.Hr()
            , HTML.H6('Copyright ©️ 2020 Richard Offer.')
        ]
        ,className="column"
        )
    ]
    )

    @app.callback( dash.dependencies.Output('pyramid-heading', 'children'), [ dash.dependencies.Input('pyramid-slider', 'value')])
    def update_pyramid_label( selected_year ):
        return "Sol Year: {}".format( selected_year )

    @app.callback( dash.dependencies.Output('status', 'figure'), [ dash.dependencies.Input('pyramid-slider', 'value'), dash.dependencies.Input('sim-selector', 'value')])
    def update_status_vline( selected_year, simulation_id ):

        if simulation_id:
            filtered_df = pop_dynamics['df'][ ( pop_dynamics['df'].simulation_id == simulation_id ) ]
        else:
            filtered_df = pop_dynamics['df']

        plot = {
            'data' : [
                dict(
                    #type="line+markers",
                    type="bar",
                    x=list(filtered_df['solday'] / 668.0),
                    y=list(100.0 * filtered_df['num_single_settlers'] / ( filtered_df['num_single_settlers'] + filtered_df['num_partnered_settlers'] ) ),
                    text=list(filtered_df['notes']),
                    hoverinfo='text',
                    hovertemplate="%{x}, %{y} - %{text}",
                    name="Single",
                    marker=dict(color='green')
                )
            ],
            'layout': {
                "xaxis" : {
                    'title': 'Sol Years'
                },
                "yaxis" : {
                    'yaxis': 'y',
                    'title': '% Single Settlers',
                    'range' : [
                        0,100.0 
                        #int(min(pop_dynamics['df']['num_single_settlers'].min(), pop_dynamics['df']['num_partnered_settlers'].min())),
                        #int(max(pop_dynamics['df']['num_single_settlers'].max(), pop_dynamics['df']['num_partnered_settlers'].max()))
                    ]
                },
                "barmode" : 'stack',
                "margin" : {'l': 40, 'b': 40, 't': 40, 'r': 40},
                "hovermode" : 'closest'
            }
        }

        if thisApp.save_plots:
            with open( "plot-settler-status.json", "w" ) as fp:

                json.dump( plot, fp )

        # only draw vertical line indicating current slider value
        # on the interactive chart

        plot['layout']['shapes'] = [{
            'type': 'line',
            'yref' : 'paper',
            'x0': selected_year,
            'y0': 0,
            'x1': selected_year,
            'y1': 1,
            'line': {
                'color': 'blue',
                'width': 3,
            }
        } ]

        return plot


    @app.callback( dash.dependencies.Output('partners', 'figure'), [ dash.dependencies.Input('pyramid-slider', 'value'), dash.dependencies.Input('sim-selector', 'value')])
    def update_partners_vline( selected_year, simulation_id ):

        if simulation_id:
            filtered_df = pop_dynamics['df'][ ( pop_dynamics['df'].simulation_id == simulation_id ) ]
        else:
            filtered_df = pop_dynamics['df']

        plot = {
            'data' : [
                dict(
                        type="line+markers",
                        x=list(filtered_df['solday'] / 668.0),
                        y=list(filtered_df['num_partnerships_started']),
                        text=list(filtered_df['notes']),
                        yaxis='y',
                        xaxis='x',
                        hoverinfo='text',
                        hovertemplate="%{x}, %{y} - %{text}",
                        name="# 'Marriages'",
                        marker=dict(color='green')
                ),
                dict(
                        type="line+markers",
                        x=list(filtered_df['solday'] / 668.0),
                        y=list(filtered_df['num_partnerships_ended']),
                        text=list(filtered_df['notes']),
                        yaxis='y',
                        xaxis='x',
                        hoverinfo='text',
                        hovertemplate="%{x}, %{y} - %{text}",
                            name="# 'Divorces'",
                            marker=dict(color='red')
                )
            ],
            'layout': {
                "xaxis" : {
                    'title': 'Sol Years'
                },
                "yaxis" : {
                    'yaxis': 'y',
                    'title': "# 'Marriages'",
                    'range' : [ 
                        int(min(pop_dynamics['df']['num_partnerships_started'].min(), pop_dynamics['df']['num_partnerships_ended'].min())),
                        int(max(pop_dynamics['df']['num_partnerships_started'].max(), pop_dynamics['df']['num_partnerships_ended'].max())),
                    ]
                },
                "margin" : {'l': 40, 'b': 40, 't': 40, 'r': 40},
                "hovermode" : 'closest'
            }
        }

        if thisApp.save_plots:
            with open( "plot-partnerships.json", "w" ) as fp:

                json.dump( plot, fp )

        # only draw vertical line indicating current slider value
        # on the interactive chart

        plot['layout']['shapes'] = [{
            'type': 'line',
            'yref' : 'paper',
            'x0': selected_year,
            'y0': 0,
            'x1': selected_year,
            'y1': 1,
            'line': {
                'color': 'blue',
                'width': 3,
            }
        } ]

        return plot


    @app.callback( dash.dependencies.Output('rates', 'figure'), [ dash.dependencies.Input('pyramid-slider', 'value'), dash.dependencies.Input('sim-selector', 'value')])
    def update_rates_vline( selected_year, simulation_id ):

        if simulation_id:
            filtered_df = pop_dynamics['df'][ ( pop_dynamics['df'].simulation_id == simulation_id ) ]
        else:
            filtered_df = pop_dynamics['df']

        plot = {
            'data' : [
                dict(
                        type="line+markers",
                        x=list(filtered_df['solday'] / 668.0),
                        y=list(filtered_df['avg_annual_birth_rate']),
                        text=list(filtered_df['simulation_id']),
                        yaxis='y',
                        xaxis='x',
                        hoverinfo='text',
                        hovertemplate="%{x}, %{y} - %{text}",
                        name="birth rate",
                        marker=dict(color='green')
                ),
                dict(
                        type="line+markers",

                        x=list(filtered_df['solday'] / 668.0),
                        y=list(filtered_df['avg_annual_death_rate']),
                        text=list(filtered_df['simulation_id']),
                        yaxis='y',
                        xaxis='x',
                        hoverinfo='text',
                        hovertemplate="%{x}, %{y} - %{text}",
                        name="death rate",
                        marker=dict(color='black')
                )
            ],
            'layout': {
                "xaxis" : {
                    'title': 'Sol Years'
                },
                "yaxis" : {
                    'yaxis': 'y',
                    'title': 'Rate per 1000 persons',
                    'range' : [ 
                        min(pop_dynamics['df']['avg_annual_birth_rate'].min(), pop_dynamics['df']['avg_annual_death_rate'].min()),
                        max(pop_dynamics['df']['avg_annual_birth_rate'].max(), pop_dynamics['df']['avg_annual_death_rate'].max())
                    ]
                },
                "margin" : {'l': 40, 'b': 40, 't': 40, 'r': 40},
                "hovermode" : 'closest'
            }
        }

        if thisApp.save_plots:
            with open( "plot-birth-rates.json", "w" ) as fp:

                json.dump( plot, fp )

        # only draw vertical line indicating current slider value
        # on the interactive chart

        plot['layout']['shapes'] = [{
            'type': 'line',
            'yref' : 'paper',
            'x0': selected_year,
            'y0': 0,
            'x1': selected_year,
            'y1': 1,
            'line': {
                'color': 'blue',
                'width': 3,
            }
        } ]

        return plot

    @app.callback( dash.dependencies.Output('population', 'figure'), [ dash.dependencies.Input('pyramid-slider', 'value')])
    def update_population_vline( selected_year ):

        plot =  {

            'data': [
                dict(
                    x=list(population['df'][ population['df']['notes'] == i]['solday'] / 668.0),
                    y=list(population['df'][ population['df']['notes'] == i]['population']),
                    text=list(population['df'][ population['df']['notes'] == i]['simulation_id']),
                    hoverinfo="all",
                    hovertemplate="%{x}, %{y} - %{text}",
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 5
                        , 'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=""
                ) for i in population['df'].notes.unique()
            ],
            'layout': {
                "xaxis" : {
                    'title': 'Sol Years',
                },
                "yaxis" : {
                    'title': 'Population'
                },
                "margin" : {'l': 40, 'b': 40, 't': 40, 'r': 40},
                "showgrid" : True,
                "hovermode" : 'closest'
            }
        }

        if thisApp.save_plots:
            with open( "plot-population.json", "w" ) as fp:

                json.dump( plot, fp )

        # only draw vertical line indicating current slider value
        # on the interactive chart

        plot['layout']['shapes'] = [{
            'type': 'line',
            'yref' : 'paper',
            'x0': selected_year,
            'y0': 0,
            'x1': selected_year,
            'y1': 1,
            'line': {
                'color': 'blue',
                'width': 3,
            }
        } ]

        return plot

    @app.callback( dash.dependencies.Output('pyramid', 'figure'), [ dash.dependencies.Input('pyramid-slider', 'value'), dash.dependencies.Input('sim-selector', 'value')])
    def update_pyramid_figure(selected_year, simulation_id):

        if simulation_id:
            filtered_df = pop_pyramid['df'][ ( pop_pyramid['df'].solday == selected_year * 668 ) & ( pop_pyramid['df'].simulation_id == simulation_id )  ]
        else:
            filtered_df = pop_pyramid['df'][ ( pop_pyramid['df'].solday == selected_year * 668 ) ]


        plot = {
            'data': [
                dict(
                        type="bar",
                        y=list(filtered_df[ filtered_df['sex'] == 'f' ]['sol_years']),
                        x=list(filtered_df[ filtered_df['sex'] == 'f' ]['value']),
                        text= list(filtered_df[ filtered_df['sex'] == 'f' ]['value']),
                        orientation='h',
                        name='F',
                        hoverinfo='text',
                        hovertemplate='%{text} Females',
                        marker=dict(color='salmon')
                ),
                dict(
                        type="bar",
                        y=list(filtered_df[ filtered_df['sex'] == 'm' ]['sol_years']),
                        x=list( -1 * filtered_df[ filtered_df['sex'] == 'm' ]['value']),
                        text=list(filtered_df[ filtered_df['sex'] == 'm' ]['value']),
                        orientation='h',
                        name='M',
                        hoverinfo='text',
                        hovertemplate='%{text} Males',
                        marker=dict(color='powderblue')
                    )
            ],
            'layout': {
                "xaxis" : {
                    'title': 'Population',
                    'tickvals' : [-500, -200, -100, -50, -25, 0, 25, 50, 100, 200, 500],
                    'ticktext' : [500, 200, 100, 50, 25, 0, 25, 50, 100, 200, 500],
                    'range' : [ 
                        int(-pop_pyramid['df']['value'].max()),
                        int(pop_pyramid['df']['value'].max()),
                    ]
                },
                "yaxis" : {'title': 'Sol Years'},
                "margin" : {'l': 40, 'b': 40, 't': 40, 'r': 40},
                "hovermode" : 'closest',
                "bargap" : 0.1,
                "barmode" : 'overlay',
            }
        }

        if thisApp.save_plots:
            with open( "plot-population-pyramid.json", "w" ) as fp:

                json.dump( plot, fp )

        return plot

    webbrowser.open( "http://127.0.0.1:8050" )

    app.run_server(debug=True)

if __name__ == '__main__':

    initialize_arguments_parser( sys.argv[1:] )

    main( sys.argv[1:] )

