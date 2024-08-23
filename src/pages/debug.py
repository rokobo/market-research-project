import dash
from dash import html, Input, Output, dcc, clientside_callback, \
    ClientsideFunction
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = html.Div([
    dbc.Stack([
        html.H1("Debug"), html.H6(id="debug-time", className="mx-auto"),
        dcc.Loading(dbc.Button(
            "Atualizar", id="refresh-debug"))
    ], direction="horizontal", className="m-2"),
    dcc.Markdown(id="debug-content", className="m-2")
])

clientside_callback(
    ClientsideFunction(
        namespace='debug',
        function_name='refresh_debugs'
    ),
    Output("debug-content", "children"),
    Output("debug-time", "children"),
    Input("refresh-debug", "n_clicks")
)
