from datetime import datetime
import dash
from dash import html, Input, Output, dcc, clientside_callback, \
    ClientsideFunction, callback
import dash_bootstrap_components as dbc
from components import diagnostics_nav
from CONFIG import CFG

dash.register_page(__name__)

layout = html.Div([
    diagnostics_nav(__name__),
    dbc.Stack([
        html.H1("Icons"), html.H6(id="icons-time", className="mx-auto"),
        dcc.Loading(dbc.Button(
            "Atualizar", id="refresh-icons"))
    ], direction="horizontal", className="m-2"),
    html.Br(),
    dbc.Row(id="icons-content", className="m-2")
])


@callback(
    Output("icons-content", "children"),
    Output("icons-time", "children"),
    Input("refresh-icons", "n_clicks")
)
def refresh_icons(n_clicks):
    out = []

    for pr in CFG.products:
        out.append(
            dbc.Stack([
                html.H6(pr.capitalize()),
                html.Img(src=f"assets/icons/{pr}-black.svg", className="ms-auto px-2"),
                html.Img(src=f"assets/icons/{pr}-red.svg", className="px-2"),
                html.Img(src=f"assets/icons/{pr}-orange.svg", className="px-2"),
                html.Img(src=f"assets/icons/{pr}-green.svg", className="px-2"),
            ], direction="horizontal")
        )

    return out, datetime.now().strftime('%H:%M:%S')
