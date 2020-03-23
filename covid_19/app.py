import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import datetime as dt

import plotly.graph_objects as go




def convert_date(str_date):
    str_to_date = dt.datetime.strptime(str_date, '%m/%d/%y')
    date_to_str = dt.datetime.strftime(str_to_date, '%Y-%m-%d')
    return  date_to_str


# loading data
covid_states = ['Confirmed', 'Deaths', 'Recovered']
urls = [f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/' \
        f'master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-{i}.csv' for i in covid_states]

CONFIRMED, DEATHS, RECOVERED = [pd.read_csv(url) for url in urls]
DAYS = list(CONFIRMED.columns)[4:]
STR_TO_DATE = {str_date: convert_date(str_date) for str_date in DAYS}

# need to rename date columns to avoid constant conversions later
[df.rename(columns=STR_TO_DATE, inplace=True) for df in [CONFIRMED, DEATHS, RECOVERED]]


def draw_infection_map(df, day):
    df = df[['Province/State', 'Country/Region', 'Lat', 'Long', day]].copy()
    df = df[df[day] != 0]
    map_trace = go.Scattergeo(
        lat=df['Lat'],
        lon=df['Long'],
        marker=dict(
            size=df[day]/50,
            sizemode='area',
            color='#D9534F'
        )
    )

    layout = go.Layout(
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
            landcolor='#ABB6C2',
            showocean=True,
            oceancolor='#4E5D6C',
            showcountries=True,
            showframe=False,
            framewidth=0,
            bgcolor='#2B3E50'
        ),
        paper_bgcolor='#4E5D6C',
        transition=dict(
            duration=500,
            easing='cubic-in-out'
        )
    )

    fig = go.Figure(data=[map_trace], layout=layout)
    return fig


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
                        dbc.CardBody(dcc.Graph(id='infection-map', figure=draw_infection_map(CONFIRMED,
                                                                                             convert_date(DAYS[-7]))))
                    ]
                )
            ],
            xl=6,
            md=6)
    ]
)

date_picker = dcc.DatePickerSingle(
    id='date-picker-single',
    date=convert_date(DAYS[-7]),
    min_date_allowed=convert_date(DAYS[0]),
    max_date_allowed=convert_date(DAYS[-1]),
    display_format='DD MMM YY'
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
        date_picker,
        charts_row,
        run_animation_button
    ],
    fluid=True
)

app.layout = html.Div(
    children=[navbar, content, html.Div(id='debug')]
)


@app.callback(
    Output('infection-map', 'figure'),
    [Input('date-picker-single', 'date')]
)
def update_map(day):
    date_only = day.split('T')[0]
    return draw_infection_map(CONFIRMED, date_only)


if __name__ == '__main__':
    app.run_server(debug=True)