import dash
from dash import html, Input, dcc, callback
import dash_bootstrap_components as dbc
from components import diagnostics_nav
from CONFIG import CFG

dash.register_page(__name__)

layout = html.Div([
    diagnostics_nav(__name__),
    dbc.Stack([
        html.H1("Ícones"), html.Div(className="mx-auto"),
    ], direction="horizontal", className="m-2"),
    html.Br(),
    dbc.Row([dbc.Stack([
        html.H6(p.capitalize()),
        html.Img(src=f"assets/icons/{p}.svg", className="ms-auto px-2"),
        html.Img(src=f"assets/icons/{p}.svg", className="px-2 icon-red"),
        html.Img(src=f"assets/icons/{p}.svg", className="px-2 icon-orange"),
        html.Img(src=f"assets/icons/{p}.svg", className="px-2 icon-green"),
    ], direction="horizontal") for p in sorted(CFG.products)], className="m-2")
])
