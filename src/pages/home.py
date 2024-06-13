import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")

layout = html.Div([
    dbc.Button("Coleta de dados", size="lg", className="me-1", href="/input"),
])
