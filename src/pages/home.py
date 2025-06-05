import dash
from dash import html
from components import navitem_with_icon
from CONFIG import CFG, BOLD
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")

layout = html.Div([
    dbc.Stack(
        [
            html.Img(src="/assets/favicon.ico", className="m-2"),
            html.H1(
                "Projeto ICB", className="m-2",
                style={"font-size": "3em"} | BOLD),
        ],
        direction="horizontal",
        class_name="m-2 bg-secondary text-white rounded-3"),
    html.H3("Páginas de Coleta", className="m-2"),
    dbc.Nav([
        navitem_with_icon(grp.capitalize(), grp, f"{i+1}-square-fill")
        for i, grp in enumerate(set(CFG.groups)) if grp is not None
    ], pills=True),
    html.Hr(),
    html.H3("Páginas de Análise", className="m-2"),
    dbc.Nav([
        navitem_with_icon("Relatórios", "report", "file-earmark-text-fill"),
        navitem_with_icon("Resultados", "result", "diagram-3-fill"),
        navitem_with_icon("Excel", "excel", "file-earmark-spreadsheet-fill"),
        navitem_with_icon("Caminhos", "paths", "pin-map-fill"),
    ], pills=True),
    html.Hr(),
    html.H3("Páginas de Administração", className="m-2"),
    dbc.Nav([
        navitem_with_icon("Marcas", "brands", "bag-dash-fill"),
    ], pills=True),
    html.Hr(),
    html.H3("Páginas de Diagnóstico", className="m-2"),
    dbc.Nav([
        navitem_with_icon(
            "Local Storage", "local-storage", "database-fill-lock"),
        navitem_with_icon("Ícones", "icons", "star-fill"),
    ], pills=True),
])
