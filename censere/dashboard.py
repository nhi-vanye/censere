
import argparse
import logging
import sys

import sqlite3
import pandas as pd

import webbrowser

import dash
import dash_core_components as DCC
import dash_html_components as HTML

from censere.config import Viewer as thisApp
from censere.config import ViewerOptions as OPTIONS

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

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

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    population = {}

    population['query'] = """
SELECT sum.*,sim.notes FROM summary sum, simulations sim
WHERE sum.simulation_id = sim.simulation_id AND sum.solday % 668 = 28
"""
    population['df'] = pd.read_sql_query( population['query'], cnx )
    population['min_range'] = 0
    population['max_range'] = int( population['df']['solday'].max() / 668.0 )


    pop_pyramid = {}

    pop_pyramid['query'] = """
SELECT pop.*, sim.notes
FROM populations pop, simulations sim
WHERE pop.simulation_id = sim.simulation_id"""

    pop_pyramid['df'] = pd.read_sql_query( pop_pyramid['query'], cnx )

    pop_pyramid['min_range'] = 0
    pop_pyramid['max_range'] = int( pop_pyramid['df']['solday'].max() / 668.0 )

    pop_dynamics = {}

    pop_dynamics['query'] = """
SELECT demo.*, sim.notes
FROM demographics demo, simulations sim
WHERE demo.simulation_id = sim.simulation_id"""

    pop_dynamics['df'] = pd.read_sql_query( pop_dynamics['query'], cnx )

    pop_dynamics['min_range'] = 0
    pop_dynamics['max_range'] = int( pop_dynamics['df']['solday'].max() / 668.0 )

    simulations = {}

    simulations['query'] = """
SELECT 
    sim.simulation_id as value,
    CASE 
        WHEN sim.notes = '' THEN sim.simulation_id 
        ELSE sim.notes || ' ' || sim.simulation_id
    END as label
FROM
    simulations sim
"""
    simulations['df'] = pd.read_sql_query( simulations['query'], cnx )
 
    simulations_list = simulations['df'].to_dict('records')

    app.layout = HTML.Div(children=[
        HTML.H1(children='Mars Censere')

        , HTML.Div(children='Population.', 
            style={
                'textAlign': 'center',
            }
        )
        , DCC.Graph(
            id='population',
            figure={
                'data' : [
                    dict(
                        x=population['df'][ population['df']['simulation_id'] == i]['solday'] / 668.0,
                        y=population['df'][ population['df']['simulation_id'] == i]['population'],
                        text=population['df'][ population['df']['simulation_id'] == i]['simulation_id'],
                        hoverinfo="all",
                        hovertemplate="%{x}, %{y}, %{text}",
                        mode='markers',
                        opacity=0.7,
                        marker={
                            'size': 5
                            , 'line': {'width': 0.5, 'color': 'white'}
                        },
                        name=""
                    ) for i in population['df'].simulation_id.unique()
                ],
                'layout': {
                    "xaxis" : {'title': 'Sol Years'},
                    "yaxis" : {'title': 'Population'},
                    "margin" : {'l': 40, 'b': 40, 't': 40, 'r': 40},
                    "showgrid" : True,
                    "hovermode" : 'closest'
                }
            }
        )
        , HTML.H2('Population Demographics')
        , HTML.Div([
            HTML.Div([
                HTML.Div([
                    HTML.Label("Year Selector", htmlFor="pyramid-slider")
                    , DCC.Slider(
                            id='pyramid-slider',
                            min=pop_pyramid['min_range'],
                            max=pop_pyramid['max_range'],
                            value=1,
                            #marks={i: '{}'.format(i) if i == 1 else str(i/668.0) for i in range(0, population['df']['solday'].max(), 6680)},
                            step=1
                        )
                    , HTML.P(id="pyramid-label")
                    , HTML.Label("Filter", htmlFor="sim-selector")
                    , DCC.Dropdown(
                            id='sim-selector',
                            options=simulations_list
                    )
                ]
                ,className="one-third column"
            )
            ])
            , HTML.Div([
                DCC.Graph(
                    id='pyramid')
                ]
                , className="two-thirds column"
            )
        ])
        , HTML.Div([
            HTML.Div([
                HTML.H2('Birth & Death Rates')
                , DCC.Graph(
                    id='rates',
                    figure={
                    'data' : [
                    dict(
                            type="line+markers",
                            x=pop_dynamics['df']['solday'] / 668.0,
                            y=pop_dynamics['df']['avg_annual_birth_rate'],
                            text=pop_dynamics['df']['simulation_id'],
                            yaxis='y',
                            xaxis='x',
                            hoverinfo='text',
                            hovertemplate="%{x}, %{y}, %{text}",
                            name="birth rate",
                            marker=dict(color='green')
                        ),
                    dict(
                            type="line+markers",
                            x=pop_dynamics['df']['solday'] / 668.0,
                            y=pop_dynamics['df']['avg_annual_death_rate'],
                            text=pop_dynamics['df']['simulation_id'],
                            yaxis='y',
                            xaxis='x',
                            hoverinfo='text',
                            hovertemplate="%{x}, %{y}, %{text}",
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
                )
                ]
                ,className="one-third column"
            )
            , HTML.Div([
                HTML.H2("Realtionships")
                , DCC.Graph(
                    id='partners',
                    figure={
                    'data' : [
                    dict(
                            type="line+markers",
                            x=pop_dynamics['df']['solday'] / 668.0,
                            y=pop_dynamics['df']['num_partnerships_started'],
                            text=pop_dynamics['df']['simulation_id'],
                            yaxis='y',
                            xaxis='x',
                            hoverinfo='text',
                            hovertemplate="%{x}, %{y}, %{text}",
                            name="# 'Marriages'",
                            marker=dict(color='green')
                        ),
                    dict(
                            type="line+markers",
                            x=pop_dynamics['df']['solday'] / 668.0,
                            y=pop_dynamics['df']['num_partnerships_ended'],
                            text=pop_dynamics['df']['simulation_id'],
                            yaxis='y',
                            xaxis='x',
                            hoverinfo='text',
                            hovertemplate="%{x}, %{y}, %{text}",
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
                                    min(pop_dynamics['df']['num_partnerships_started'].min(), pop_dynamics['df']['num_partnerships_ended'].min()),
                                    max(pop_dynamics['df']['num_partnerships_started'].max(), pop_dynamics['df']['num_partnerships_ended'].max()),
                                ]
                            },
                            "margin" : {'l': 40, 'b': 40, 't': 40, 'r': 40},
                            "hovermode" : 'closest'
                        }
                    }
                )
            ]
            ,className="one-third column"
            )
            , HTML.Div([
                HTML.H2("Settler Status")
                , DCC.Graph(
                    id='status',
                    figure={
                    'data' : [
                    dict(
                            type="line+markers",
                            x=pop_dynamics['df']['solday'] / 668.0,
                            y=pop_dynamics['df']['num_single_settlers'],
                            text=pop_dynamics['df']['simulation_id'],
                            hoverinfo='text',
                            hovertemplate="%{x}, %{y}, %{text}",
                            name="Single",
                            marker=dict(color='blue')
                        ),
                    dict(
                            type="line+markers",
                            x=pop_dynamics['df']['solday'] / 668.0,
                            y=pop_dynamics['df']['num_partnered_settlers'],
                            text=pop_dynamics['df']['simulation_id'],
                            hoverinfo='text',
                            hovertemplate="%{x}, %{y}, %{text}",
                            name="'Married'",
                            marker=dict(color='black')
                        )
                        ],
                        'layout': {
                            "xaxis" : {
                                'title': 'Sol Years'
                            },
                            "yaxis" : {
                                'yaxis': 'y',
                                'title': '# Settlers',
                                'range' : [ 
                                    min(pop_dynamics['df']['num_single_settlers'].min(), pop_dynamics['df']['num_partnered_settlers'].min()),
                                    max(pop_dynamics['df']['num_single_settlers'].max(), pop_dynamics['df']['num_partnered_settlers'].max())
                                ]
                            },
                            "margin" : {'l': 40, 'b': 40, 't': 40, 'r': 40},
                            "hovermode" : 'closest'
                        }
                    }
                )
            ]
            ,className="one-third column"
            )        
        ])
    ]
    )

    @app.callback( dash.dependencies.Output('pyramid-label', 'children'), [ dash.dependencies.Input('pyramid-slider', 'value')])
    def update_pyramid_label( selected_year ):
        return "Sol Year: {}".format( selected_year )

    @app.callback( dash.dependencies.Output('population', 'children'), [ dash.dependencies.Input('pyramid-slider', 'value')])
    def update_population_vline( selected_year ):
        return "Sol Year: {}".format( selected_year )

    @app.callback( dash.dependencies.Output('pyramid', 'figure'), [ dash.dependencies.Input('pyramid-slider', 'value')])
    def update_pyramid_figure(selected_year):

        filtered_df = pop_pyramid['df'][ pop_pyramid['df'].solday == selected_year * 668]

        data = [
            dict(
                    type="bar",
                    y=filtered_df[ filtered_df['sex'] == 'f' ]['sol_years'],
                    x=filtered_df[ filtered_df['sex'] == 'f' ]['value'],
                    text= filtered_df[ filtered_df['sex'] == 'f' ]['value'],
                    orientation='h',
                    name='F',
                    hoverinfo='text',
                    hovertemplate='%{text} Females',
                    marker=dict(color='salmon')
                ),
            dict(
                    type="bar",
                    y=filtered_df[ filtered_df['sex'] == 'm' ]['sol_years'],
                    x= -1 * filtered_df[ filtered_df['sex'] == 'm' ]['value'],
                    text= filtered_df[ filtered_df['sex'] == 'm' ]['value'],
                    orientation='h',
                    name='M',
                    hoverinfo='text',
                    hovertemplate='%{text} Males',
                    marker=dict(color='powderblue')
                )
        ]

        return {
            'data': data,
            'layout': {
                "xaxis" : {
                    'title': 'Population',
                    'tickvals' : [-500, -200, -100, -50, -25, 0, 25, 50, 100, 200, 500],
                    'ticktext' : [500, 200, 100, 50, 25, 0, 25, 50, 100, 200, 500],
                    'range' : [ 
                        -pop_pyramid['df']['value'].max(),
                        pop_pyramid['df']['value'].max(),
                    ]
                },
                "yaxis" : {'title': 'Sol Years'},
                "margin" : {'l': 40, 'b': 40, 't': 40, 'r': 40},
                "hovermode" : 'closest',
                "bargap" : 0.1,
                "barmode" : 'overlay',
            }
        }

    webbrowser.open( "http://127.0.0.1:8050" )

    app.run_server(debug=True)

if __name__ == '__main__':

    initialize_arguments_parser( sys.argv[1:] )

    main( sys.argv[1:] )

