import dash
from dash import html, Input, Output, dcc, clientside_callback, \
    ClientsideFunction
import dash_bootstrap_components as dbc
from components import diagnostics_nav

dash.register_page(__name__)

layout = html.Div([
    diagnostics_nav(__name__),
    dbc.Stack([
        html.H1("Local Storage"), html.H6(id="local_storage-time", className="mx-auto"),
        dcc.Loading(dbc.Button(
            "Atualizar", id="refresh-local_storage"))
    ], direction="horizontal", className="m-2"),
    dcc.Markdown(id="local_storage-content", className="m-2")
])

clientside_callback(
    ClientsideFunction(
        namespace='functions',
        function_name='refresh_local_storages'
    ),
    Output("local_storage-content", "children"),
    Output("local_storage-time", "children"),
    Input("refresh-local_storage", "n_clicks")
)
