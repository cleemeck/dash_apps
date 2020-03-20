import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

import plotly.graph_objects as go





CONFIRMED = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/'
                        'master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv')
DEATHS = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/'
                  'master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv')
RECOVERED = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/'
                        'master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv')

DAYS = dict(enumerate(list(CONFIRMED.columns)[4:]))

LAST_UPDATE = CONFIRMED.columns[-1]

trace_first = go.Scattergeo(
    lat=CONFIRMED['Lat'],
    lon=CONFIRMED['Long'],
    marker=dict(
        size=CONFIRMED.iloc[:, 4] / 50,
        sizemin=2,
        sizemode='area'),
    text=CONFIRMED.iloc[:,4])

frames = [
    go.Frame(
        data=[go.Scattergeo(
            lat=CONFIRMED['Lat'],
            lon=CONFIRMED['Long'],
            marker=dict(
                size=CONFIRMED.iloc[:,i] / 50,
                sizemin=2,
                sizemode='area'),
            text=CONFIRMED.iloc[:,i]
            )
        ]
    )
    for i in range(5,CONFIRMED.shape[1])]

layout = go.Layout(
    margin=dict(l=0, r=0, t=0, b=0),
    geo=dict(
        landcolor='#4E5D6C',
        showocean=True,
        oceancolor='#4E5D6C',
        showcountries=True,
        showframe=False,
        framewidth=0,
        bgcolor='#2B3E50'
    ),
    paper_bgcolor='#4E5D6C',
    updatemenus=[
        dict(
            type='buttons',
            buttons=[dict(label='Play', method='animate', args=[None])]
        )]
)

fig = go.Figure(data=[trace_first], layout=layout, frames=frames)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])

navbar = dbc.NavbarSimple(
    brand="COVID-19 Data Exploration",
    brand_href="#",
    color="secondary",
    dark=True,
    fluid=True
)

kpi_row = dbc.Row(
    children=[
        dbc.Col(
            dbc.Card(
                children=[
                    dbc.CardHeader(html.Div('Confirmed Cases')),
                    dbc.CardBody(html.H4(np.sum(CONFIRMED.iloc[:, -1])))
                ],
                color='danger'
            )
        ),
        dbc.Col(
            dbc.Card(
                children=[
                    dbc.CardHeader(html.Div('Deaths')),
                    dbc.CardBody(html.H4(np.sum(DEATHS.iloc[:, -1])))
                ],
                color='dark'
            )
        ),
        dbc.Col(
            dbc.Card(
                children=[
                    dbc.CardHeader(html.Div('Recovered')),
                    dbc.CardBody(html.H4(np.sum(RECOVERED.iloc[:, -1])))
                ],
                color='success'
            )
        )
    ]
)

charts_row = dbc.Row(
    children=[
        dbc.Col(
            children=[
                dbc.Card(
                    children=[
                        dbc.CardHeader(html.Div('Confirmed Map')),
                        dbc.CardBody(dcc.Graph(figure=fig))
                    ]
                )
            ],
            xl=6,
            md=6)
    ]
)

day_slider = dcc.Slider(
    id='day-slider',
    min=0,
    max=len(DAYS),
    value=0,
    marks={
        k: v for k, v in DAYS.items()
    }
)

run_animation_button = dbc.Button(
    id='run-animation-button',
    n_clicks=0,
    children=['Run Animation'],
    color='primary'
)

content = dbc.Container(
    children=[
        kpi_row,
        day_slider,
        run_animation_button
    ],
    fluid=True
)

app.layout = html.Div(
    children=[navbar, content]
)


@app.callback(
    Output('day-slider', 'value'),
    [Input('run-animation-button', 'n_clicks')],
    [State('day-slider', 'value')]
)
def update_slider(n_clicks, value):
    return value + 1


if __name__=='__main__':
    app.run_server(debug=True)