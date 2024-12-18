# flake8: noqa: E501
import dash
from dash import html, callback, Input, Output, State, dcc, \
    clientside_callback, ClientsideFunction
from CONFIG import BOLD, CFG, COORDINATES
import dash_bootstrap_components as dbc
from os import getenv
import dash_ag_grid as dag
from dotenv import load_dotenv
from components import adm_nav
from tools import path_map


dash.register_page(__name__)
load_dotenv()


layout = html.Div([
    adm_nav(__name__),
    dbc.Alert([
        html.H5([
            html.I(className="bi bi-info-circle-fill"),
            " Instruções e definições", html.Hr(className="m-1")
        ], className="alert-heading", style=BOLD),
        dcc.Markdown(
            '''Só é possível atualizar quando a senha correta está no campo abaixo. Somente use quando necessário!''',
        style={'whiteSpace': 'pre-line'}, className="mb-0")
    ], dismissable=False, color="warning"),
    dbc.Stack([
        html.H1("Caminhos"), html.Div(className="mx-auto"),
        dcc.Loading(dbc.Button(
            "Atualizar dados", id="refresh-paths", disabled=True))
    ], direction="horizontal", className="m-2"),
    dbc.Row(
        dbc.Input(
            id="password-paths", type="text", debounce=True,
            placeholder="Senha de administrador", persistence=True,
            persistence_type="local"
    ), className="m-2"),
    dbc.Row(dcc.Graph(
        id="paths-map", style={"height": "70vh", "width": "100%"}
    ), className="m-2")
], className="mb-20")


@callback(
    Output("refresh-paths", "disabled"),
    Input("password-paths", "value")
)
def enable_refresh(password):
    ADM_PASSWORD = getenv("ADM_PASSWORD")
    return not ((password == ADM_PASSWORD) and (ADM_PASSWORD is not None))

@callback(
    Output("paths-map", "figure"),
    Input("refresh-paths", "n_clicks"),
    prevent_initial_call=True
)
def update_paths(n_clicks):
    return path_map(show=False)
