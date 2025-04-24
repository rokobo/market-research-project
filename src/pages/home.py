import dash
from dash import html, callback, Input, Output, State, ALL, dcc, \
    clientside_callback, ClientsideFunction
from components import product_grid, wait_modal, INFO, CLEAR
from tools import load_establishments, save_products
from CONFIG import CFG, ICONS, BOLD, CENTER, UNDERLINE
import dash_bootstrap_components as dbc
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
import dash_mantine_components as dmc

dash.register_page(__name__, path="/")

layout = html.Div([
    html.H3("Selecione a categoria de produtos", style=CENTER, className="m-2"),
    dbc.Nav([
        dbc.NavItem(dbc.NavLink(
            grp.capitalize(), href=f"/categoria/{grp}",
            active=True, class_name="m-2 p-3",
        )) for grp in set(CFG.groups) if grp is not None
    ], class_name="m-2", pills=True),
    html.Hr(),
    html.H3("Páginas informativas", style=CENTER, className="m-2"),
    dbc.Nav([
        dbc.NavItem(dbc.NavLink(
            "Relatórios", href="/report",
            active=True, class_name="m-2 p-3",
        )),
        dbc.NavItem(dbc.NavLink(
            "Resultados", href="/result",
            active=True, class_name="m-2 p-3",
        )),
        dbc.NavItem(dbc.NavLink(
            "Excel", href="/excel",
            active=True, class_name="m-2 p-3",
        )),
        dbc.NavItem(dbc.NavLink(
            "Caminhos", href="/paths",
            active=True, class_name="m-2 p-3",
        )),
    ], class_name="m-2", pills=True),
])
