import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from app import app
import pandas as pd
import numpy as np
import datetime as dt


def convert_date(str_date):
    str_to_date = dt.datetime.strptime(str_date, '%m/%d/%y')
    date_to_str = dt.datetime.strftime(str_to_date, '%Y-%m-%d')
    return date_to_str


# loading data
covid_states = ['Confirmed', 'Deaths', 'Recovered']

urls = [f'https://raw.githubusercontent.com/bumbeishvili/'
        f'covid19-daily-data/master/time_series_19-covid-{i}.csv'
        for i in covid_states]


CONFIRMED, DEATHS, RECOVERED = [pd.read_csv(url) for url in urls]
DAYS = list(CONFIRMED.columns)[4:]
STR_TO_DATE = {str_date: convert_date(str_date) for str_date in DAYS}

# need to rename date columns to avoid constant conversions later
[df.rename(columns=STR_TO_DATE, inplace=True) for df in [CONFIRMED, DEATHS, RECOVERED]]

ALL_DFS = [CONFIRMED, DEATHS, RECOVERED]


def draw_infection_map(df, day):
    df = df[['Province/State', 'Country/Region', 'Lat', 'Long', day]].copy()
    df = df[df[day] != 0]
    map_trace = go.Scattergeo(
        lat=df['Lat'],
        lon=df['Long'],
        marker=dict(
            size=abs(df[day]/50),
            sizemode='area',
            color='#D9534F'
        )
    )


    layout = go.Layout(
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
            landcolor='#abb6c2',
            showocean=True,
            oceancolor='#abb6c2',
            showcountries=True,
            showframe=False,
            framewidth=0,
            bgcolor='#abb6c2'
        ),
        paper_bgcolor='#abb6c2',
        transition=dict(
            duration=500,
            easing='cubic-in-out'
        )
    )

    fig = go.Figure(data=[map_trace], layout=layout)
    return fig


def draw_curve(df1, df2, day):
    day_idx = list(df1.columns).index(day) + 1

    df1_curve_trace = go.Bar(
        x=DAYS,
        y=list(np.sum(df1.iloc[:, 4:day_idx].copy(), axis=0)),
        name='Confirmed',
        marker=dict(
            color='#d9534f')
    )
    df2_curve_trace = go.Bar(
        x=DAYS,
        y=list(np.sum(df2.iloc[:, 4:day_idx].copy(), axis=0)),
        width=0.4,
        name='Recovered',
        marker=dict(
            color='#5cb85c')
    )
    curve_layout = go.Layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='#abb6c2',
        plot_bgcolor='#abb6c2',
        barmode='overlay',
        xaxis=dict(
            range=[DAYS[0], DAYS[-1]],
            fixedrange=True))
    fig = go.Figure([df1_curve_trace, df2_curve_trace], curve_layout)
    return fig


def render_kpi_card(covid_state, color):
    kpi_card = dbc.Col(dbc.Card(
        children=[
            dbc.CardHeader(html.H4(covid_state), className='text-center'),
            dbc.CardBody(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                children=[
                                    html.Div('Total', className='text-center'),
                                    html.Div(id=f'{covid_state}-total', className='display-4 text-center')
                                ]
                            ),
                            dbc.Col(
                                children=[
                                    html.Div('Daily Change', className='text-center'),
                                    html.Div(id=f'{covid_state}-change', className='display-4 text-center')
                                ]
                            )
                        ]
                    )
                ]
            ),
        ],
        color=color
    )
    )
    return kpi_card


kpi_row = dbc.Row(
    children=[
        render_kpi_card(covid_state, color)
        for covid_state, color
        in zip(covid_states, ['danger', 'dark', 'success'])
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
    date=convert_date(DAYS[-1]),
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
        dbc.Col([dcc.Graph(figure=draw_curve(CONFIRMED, RECOVERED, '2020-03-26'))], width=6)
    ],
    fluid=True
)

layout = html.Div(
    children=[content, html.Div(id='debug')]
)


@app.callback(
    Output('infection-map', 'figure'),
    [Input('date-picker-single', 'date')]
)
def update_map(day):
    date_only = day.split('T')[0]
    return draw_infection_map(CONFIRMED, date_only)


@app.callback(
    [Output(f'{covid_state}-total', 'children') for covid_state in covid_states],
    [Input('date-picker-single', 'date')]
)
def update_total(day):
    date_only = day.split('T')[0]
    return ['{:,.0f}'.format(np.sum(df[date_only])).replace(',', ' ')
            for df in ALL_DFS]


@app.callback(
    [Output(f'{covid_state}-change', 'children') for covid_state in covid_states],
    [Input('date-picker-single', 'date')]
)
def update_change(day):
    date_only = day.split('T')[0]
    selected_idx = [list(df.columns).index(date_only) for df in ALL_DFS]
    results = [np.sum(df.iloc[:, idx]) - np.sum(df.iloc[:, idx-1])
               for df, idx in zip(ALL_DFS, selected_idx)]
    return ['{:+,.0f}'.format(result).replace(',', ' ') for result in results]
