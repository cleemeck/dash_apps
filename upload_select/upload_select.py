import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_table as dt
import datetime
import pandas as pd
import base64
import io


DATA_TYPES = ['object', 'enum']


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), nrows=100)
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), nrows=100)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df.to_json(date_format='iso', orient='split'), filename


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])


app.layout = dbc.Container(
    children=[
        dbc.Row(
            dbc.Card(
                children=[
                    dbc.CardHeader('Step 1', className='card-title'),
                    dbc.CardBody(
                        children=[
                            dcc.Upload(
                                children=[
                                    dbc.Row(
                                        children=[
                                            html.Div('Drag and drop or '),
                                            dbc.Button('Browse Files')
                                        ],
                                        align='center',
                                        justify='center'
                                    )
                                ],
                                id='upload-data'
                            )
                        ]
                    )
                ],
                style={'width': '100%'}
            )
        ),
        dbc.Row(
            children=[
                dbc.Card(
                    children=[
                        dbc.CardHeader('Step 2', className='card-title'),
                        dbc.CardBody()
                    ],
                    style={'width': '100%'}
                )
            ],
            style={'display': 'none'}
        )
    ]
)


if __name__ == '__main__':
    app.run_server(debug=True)