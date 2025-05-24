import dash
from dash import html, callback, Input, Output, State, ALL, dcc, \
    clientside_callback, ClientsideFunction
from components import wait_modal, INFO, navitem_with_icon
from tools import load_establishments, save_products
from CONFIG import CFG, ICONS, BOLD, CENTER, UNDERLINE
import dash_bootstrap_components as dbc
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
import dash_mantine_components as dmc

dash.register_page(__name__, path="/")

layout = html.Div([
    dbc.Stack([
        html.Img(src="/assets/favicon.ico", className="m-2"),
        html.H1("Projeto ICB", className="m-2"),
    ], direction="horizontal"),
    html.Br(),
    html.H3("+ Páginas de coleta", className="m-2"),
    dbc.Nav([
        navitem_with_icon(grp.capitalize(), grp, f"{i}-square-fill")
        for i, grp in enumerate(set(CFG.groups)) if grp is not None
    ], class_name="m-2", pills=True),
    html.Hr(),
    html.H3("+ Páginas informativas", className="m-2"),
    dbc.Nav([
        navitem_with_icon("Relatórios", "report", "file-earmark-text-fill"),
        navitem_with_icon("Resultados", "result", "diagram-3-fill"),
        navitem_with_icon("Excel", "excel", "file-earmark-spreadsheet-fill"),
        navitem_with_icon("Caminhos", "paths", "pin-map-fill"),
    ], class_name="m-2", pills=True),
    html.Hr(),
    html.H3("+ Páginas administrativas", className="m-2"),
    dbc.Nav([
        navitem_with_icon("Marcas", "brands", "bag-dash-fill"),
    ], class_name="m-2", pills=True),
])
