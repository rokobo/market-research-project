"""Components for the pages."""

import dash_bootstrap_components as dbc
from dash import html
from typing import Optional

def text_input(
    label: str, input_type: str, placeholder: str,
    id_name: str, formtext: Optional[str] = None
) -> html.Div:
    elements = [
        dbc.Label(label),
        dbc.Input(type=input_type, id=id_name, placeholder=placeholder),
    ]
    if formtext:
        elements.append(dbc.FormText(formtext, color="secondary"))
    return html.Div(elements, className="m-3")
