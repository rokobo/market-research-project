import dash
from dash import html, dcc
from components import text_input

dash.register_page(__name__)

layout = html.Div([
    html.H1("input"),
    text_input("Nome do coletor", "text", "...", "nome")

])
