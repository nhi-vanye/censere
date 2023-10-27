#! /usr/bin/env python3

## Copyright (c) 2019,2023 Richard Offer. All right reserved.
#
# see LICENSE.md for license details


from __future__ import division

import click

import logging
import sys

import sqlite3
import pandas as pd

import webbrowser
import json

from dash import Dash, dcc, html, dash_table, callback, Output, Input

from censere.config import thisApp


@click.command("dashboard")
@click.pass_context
@click.option("--save-plots",
        is_flag=True,
        default=False,
        help="Save the plot descriptions into local files for use by orca (CENSERE_DASHBOARD_SAVE_PLOTS)")
def cli( ctx, save_plots ):
    """Interactive UI for viewing simulation results"""

    thisApp.save_plots = save_plots

    cnx = sqlite3.connect( thisApp.database )

    app = Dash("Mars Censere dashboard")

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
 
    app.layout = html.Div(children=[
        html.H1(children='Mars Censere')

        , html.H4('Overall Population')
        , dcc.Graph( id='population')
        , html.P("")
        , dash_table.DataTable(
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
        , html.H4('Population Demographics')
        , html.Div([
            html.Div([
                html.Div([
                    html.Label("Year Selector", htmlFor="pyramid-slider")
                    , dcc.Slider(
                            id='pyramid-slider',
                            min=pop_pyramid['min_range'],
                            max=pop_pyramid['max_range'],
                            value=0,
                            step=1
                        )
                    #, html.P(id="pyramid-label")
                    , html.Label("Filter", htmlFor="sim-selector")
                    , dcc.Dropdown(
                            id='sim-selector',
                            options=simulations_list
                    )
                ]
                ,className="one-half column"
            )
            ])
            , html.Div([
                html.P(id="pyramid-heading")
                , dcc.Graph( id='pyramid')
                ]
                , className="one-half column"
            )
        ])
        , html.Div([
            html.Div([
                html.H4('Birth & Death Rates')
                , dcc.Graph( id='rates')
                ]
                ,className="one-third column"
            )
            , html.Div([
                html.H4("Realtionships")
                , dcc.Graph( id='partners')
            ]
            ,className="one-third column"
            )
            , html.Div([
                html.H4("Settler Status")
                , dcc.Graph( id='status' )
            ]
            ,className="one-third column"
            )        
        ])
        , html.Div(id='simulation-id', style={'display': 'none'})
        , html.Div([
            html.Hr()
            , html.H6('Copyright ©️ 2020,2023 Richard Offer.')
        ]
        ,className="column"
        )
    ]
    )

    @callback( Output('pyramid-heading', 'children'), [ Input('pyramid-slider', 'value')])
    def update_pyramid_label( selected_year ):
        return "Sol Year: {}".format( selected_year )

    @callback( Output('status', 'figure'), [ Input('pyramid-slider', 'value'), Input('sim-selector', 'value')])
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


    @callback( Output('partners', 'figure'), [ Input('pyramid-slider', 'value'), Input('sim-selector', 'value')])
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


    @callback( Output('rates', 'figure'), [ Input('pyramid-slider', 'value'), Input('sim-selector', 'value')])
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

    @callback( Output('population', 'figure'), [ Input('pyramid-slider', 'value')])
    def update_population_vline( selected_year ):

        plot =  {

            'data': [
                dict(
                    x=list(population['df'][ population['df']['unique_notes'] == i]['solday'] / 668.0),
                    y=list(population['df'][ population['df']['unique_notes'] == i]['population']),
                    text=list(population['df'][ population['df']['unique_notes'] == i]['simulation_id']),
                    hoverinfo="all",
                    hovertemplate="%{x}, %{y} - %{text}",
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 5
                        , 'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=""
                ) for i in population['df'].unique_notes.unique()
                
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

        """
        plot["data"].append( 
            dict(
                x=list(population['df']['solday'] / 668.0),
                y=list(population['df'].mean( population['df']['population'] )),
                marker={
                    'size': 5
                    ,'line': {'width': 0.5, 'color': 'black'}
                    },
                name=""
                )

            )
        """

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

    @callback( Output('pyramid', 'figure'), [ Input('pyramid-slider', 'value'), Input('sim-selector', 'value')])
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

