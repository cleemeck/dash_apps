import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import flask
from app import app
from apps import about, daily_dashboard, animations

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#4E5D6C",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

PAGES = ['about', 'daily-dashboard', 'animations']

sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("About", href="/about", id="about-link"),
                dbc.NavLink("Daily Dashboard", href="/daily-dashboard", id="daily-dashboard-link"),
                dbc.NavLink("Animations", href="/animations", id="animations-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,
    content
])


def serve_layout():
    if flask.has_request_context():
        return url_bar_and_content_div
    return html.Div([
        url_bar_and_content_div,
        about.layout,
        daily_dashboard.layout
    ])


app.layout = serve_layout

# Index callbacks
# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on


@app.callback(
    [Output(f"{page}-link", "active") for page in PAGES],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f'/{page}' for page in PAGES]


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/about"]:
        return about.layout
    elif pathname == "/daily-dashboard":
        return daily_dashboard.layout
    elif pathname == "/animations":
        return animations.layout
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == '__main__':
    app.run_server(debug=True)