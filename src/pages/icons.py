import dash
from dash import html, Input, dcc, callback
import dash_bootstrap_components as dbc
from components import diagnostics_nav
from CONFIG import CFG
from tools import create_icon_variations

dash.register_page(__name__)

layout = html.Div([
    diagnostics_nav(__name__),
    dbc.Stack([
        html.H1("Ícones"), html.Div(className="mx-auto"),
        dcc.Loading(dbc.Button(
            "Atualizar", id="refresh-icons"))
    ], direction="horizontal", className="m-2"),
    html.Br(),
    dbc.Row([dbc.Stack([
        html.H6(p.capitalize()),
        html.Img(src=f"assets/icons/{p}-black.svg", className="ms-auto px-2"),
        html.Img(src=f"assets/icons/{p}-red.svg", className="px-2"),
        html.Img(src=f"assets/icons/{p}-orange.svg", className="px-2"),
        html.Img(src=f"assets/icons/{p}-green.svg", className="px-2"),
    ], direction="horizontal") for p in sorted(CFG.products)], className="m-2")
])


@callback(
    Input("refresh-icons", "n_clicks")
)
def refresh_icons(n_clicks):
    create_icon_variations()
