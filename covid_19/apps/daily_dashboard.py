import dash
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
COVID_STATES = ['Confirmed', 'Deaths', 'Recovered']
COVID_COLORS = ['warning', 'danger', 'success']


urls = [f'https://raw.githubusercontent.com/bumbeishvili/'
        f'covid19-daily-data/master/time_series_19-covid-{i}.csv'
        for i in COVID_STATES]


CONFIRMED, DEATHS, RECOVERED = [pd.read_csv(url) for url in urls]
DAYS = list(CONFIRMED.columns)[4:]
STR_TO_DATE = {str_date: convert_date(str_date) for str_date in DAYS}

# need to rename date columns to avoid constant conversions later
[df.rename(columns=STR_TO_DATE, inplace=True) for df in [CONFIRMED, DEATHS, RECOVERED]]

ALL_DFS = [CONFIRMED, DEATHS, RECOVERED]
DAYS_FOR_DISPLAY = list(CONFIRMED.columns)


def draw_infection_map(df, day):
    df = df[['Province/State', 'Country/Region', 'Lat', 'Long', day]].copy()
    df = df[df[day] != 0]
    map_trace = go.Scattergeo(
        lat=df['Lat'],
        lon=df['Long'],
        marker=dict(
            size=abs(df[day]/50),
            sizemode='area',
            color='#f0ad4e'
        )
    )


    layout = go.Layout(
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
            projection=dict(type='natural earth'),
            landcolor='#4E5D6C',
            showocean=True,
            oceancolor='#4E5D6C',
            showcountries=True,
            countrycolor='#868e96',
            coastlinecolor='#868e96',
            showframe=False,
            framewidth=0,
            bgcolor='#4E5D6C'
        ),
        paper_bgcolor='#4E5D6C',
        transition=dict(
            duration=500,
            easing='cubic-in-out'
        )
    )

    fig = go.Figure(data=[map_trace], layout=layout)
    return fig


def draw_curve(df1, df2, df3,  day):
    day_idx = list(df1.columns).index(day) + 1

    df1_curve_trace = go.Scatter(
        x=list(df1.columns)[4:],
        y=list(np.sum(df1.iloc[:, 4:day_idx].copy(), axis=0)),
        mode='lines+markers',
        name='Confirmed',
        marker=dict(
            color='#f0ad4e')
    )

    df2_curve_trace = go.Scatter(
        x=list(df2.columns)[4:],
        y=list(np.sum(df2.iloc[:, 4:day_idx].copy(), axis=0)),
        mode='lines+markers',
        name='Deaths',
        marker=dict(
            color='#d9534f')
    )

    df3_curve_trace = go.Bar(
        x=list(df3.columns)[4:],
        y=list(np.sum(df3.iloc[:, 4:day_idx].copy(), axis=0)),
        name='Recovered',
        marker=dict(
            color='#5cb85c')
    )

    curve_layout = go.Layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='#4E5D6C',
        plot_bgcolor='#4E5D6C',
        barmode='overlay',
        xaxis=dict(
            color='#fff',
            zeroline=False,
            title=dict(
                text='Date')
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            color='#fff',
            title=dict(
                text='Number of Cases')
        ),
        legend=dict(
            x=0.7,
            font=dict(
                color='#fff'
            )))
    fig = go.Figure([df1_curve_trace, df2_curve_trace, df3_curve_trace], curve_layout)
    return fig


def render_kpi_card(covid_state, color):
    kpi_card = dbc.Col(
        dbc.Card(
            children=[
                dbc.CardHeader(html.H4(covid_state), style={'font-size': '1.1vw', 'text-align': 'center'}),
                dbc.CardBody(
                    children=[
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    children=[
                                        html.Div('Total',
                                                 style={'font-size': '1vw', 'text-align': 'center'}),
                                        html.Div(id=f'{covid_state}-total',
                                                 style={'font-size': '2.5vw', 'text-align': 'center'})
                                    ]
                                ),
                                dbc.Col(
                                    children=[
                                        html.Div('Daily Change',
                                                 style={'font-size': '1vw', 'text-align': 'center'}),
                                        html.Div(id=f'{covid_state}-change',
                                                 style={'font-size': '2.5vw', 'text-align': 'center'})
                                    ]
                                )
                            ]
                        )
                    ]
                ),
            ],
            color=color,
            className='mb-3 mt-3'
        )
    )
    return kpi_card


dashboard_nav = dbc.NavbarSimple(
    children=[
        dbc.Button(
            '<',
            id='previous-day-button',
            color='primary',
            className='mr-1'
        ),
        dcc.DatePickerSingle(
            id='date-picker-single',
            date=convert_date(DAYS[-1]),
            min_date_allowed=convert_date(DAYS[0]),
            max_date_allowed=convert_date(DAYS[-1]),
            display_format='DD MMM YYYY'
        ),
        dbc.Button(
            '>',
            id='next-day-button',
            color='primary',
            className='ml-1'
        )
    ],
    brand='Daily COVID-19 Numbers',
    color='dark',
    dark=True,
    fluid=True,
    sticky='top'
)

kpi_row = dbc.Row(
    children=[
        render_kpi_card(covid_state, color)
        for covid_state, color
        in zip(COVID_STATES, COVID_COLORS)
        ]
)

charts_deck = dbc.CardDeck(
            children=[
                dbc.Card(
                    children=[
                        dbc.CardHeader(
                            dbc.Row(
                                children=[
                                    html.H5('Confirmed Cases', className='card-title', style={'text-align': 'center'}),
                                    dbc.Popover(
                                        children=[
                                            dbc.PopoverHeader('Infection Map'),
                                            dbc.PopoverBody('Area of the bubble is related to acumulative '
                                                            'number of cases in the region / country. Hover over '
                                                            'to see the actual numbers. Scroll to zoom in/out '
                                                            'and double click to reset view.')
                                        ],
                                        id='map-popover',
                                        is_open=False,
                                        target='map-popover-target'
                                    ),
                                    dbc.Button('?', id='map-popover-target', className='button', color='info')
                                ],
                                align='center',
                                justify='between',
                                className='pl-2 pr-2'
                        )),
                        dbc.CardBody(
                            children=[
                                dcc.Graph(
                                    id='infection-map',
                                    figure=draw_infection_map(CONFIRMED, convert_date(DAYS[-7])),
                                    config=dict(
                                        displayModeBar=True
                                    )
                            )],
                        )
                    ]
                ),
                dbc.Card(
                    children=[
                        dbc.CardHeader(html.H5('The famous curve', className='card-title')),
                        dbc.CardBody(
                            children=[
                                dcc.Graph(
                                    figure=draw_curve(CONFIRMED, DEATHS, RECOVERED, list(CONFIRMED.columns)[-1]),
                                    id='curve-scatter')
                            ],
                        )
                    ]
                )
            ],
)

content = html.Div(
    children=[
        dashboard_nav,
        dbc.Container(
            children=[
                kpi_row,
                charts_deck
            ],
            fluid=True
        )
    ]
)

layout = html.Div(
    children=[content, html.Div('TEST', id='debug', style={'height': '1000px'})]
)


@app.callback(
    [Output('infection-map', 'figure'),
     Output('curve-scatter', 'figure')],
    [Input('date-picker-single', 'date')]
)
def update_map(day):
    date_only = day.split('T')[0]
    return draw_infection_map(CONFIRMED, date_only), draw_curve(CONFIRMED, DEATHS, RECOVERED, date_only)


@app.callback(
    [Output(f'{covid_state}-total', 'children') for covid_state in COVID_STATES],
    [Input('date-picker-single', 'date')]
)
def update_total(day):
    date_only = day.split('T')[0]
    return ['{:,.0f}'.format(np.sum(df[date_only]))
            for df in ALL_DFS]


@app.callback(
    [Output(f'{covid_state}-change', 'children') for covid_state in COVID_STATES],
    [Input('date-picker-single', 'date')]
)
def update_change(day):
    date_only = day.split('T')[0]
    selected_idx = [list(df.columns).index(date_only) for df in ALL_DFS]
    results = [np.sum(df.iloc[:, idx]) - np.sum(df.iloc[:, idx-1])
               for df, idx in zip(ALL_DFS, selected_idx)]
    return ['{:+,.0f}'.format(result) for result in results]


@app.callback(
    Output("map-popover", "is_open"),
    [Input("map-popover-target", "n_clicks")],
    [State("map-popover", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    [Output('date-picker-single', 'date')],
    [Input('previous-day-button', 'n_clicks'),
     Input('next-day-button', 'n_clicks')],
    [State('date-picker-single', 'date')]
)
def move_date(prev_day, next_day, current_date):
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    # if prev_day is not None:
        available_dates = list(STR_TO_DATE.values())
        date_idx = available_dates.index(current_date)
        if button_id == 'previous-day-button':
            if date_idx - 1 >=0:
                date_idx -= 1
        elif button_id == 'next-day-button':
            if date_idx + 1 <= len(available_dates)-1:
                date_idx += 1

    return [available_dates[date_idx]]