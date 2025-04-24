import dash
from dash import html
from components import create_page
from CONFIG import CFG

dash.register_page(__name__, path_template="/categoria/<group>")


def layout(group=None):
    if group in set(CFG.groups) and group is not None:
        return create_page(group)
    else:
        return html.H1("Grupo não encontrado", style={"color": "red"})
