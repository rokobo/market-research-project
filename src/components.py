"""Components for the pages."""

import dash_bootstrap_components as dbc
from dash import html
from tools import load_brands
from CONFIG import CFG, ICONS, BOLD, CENTER
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML


def create_product_form(
    id_name: str, idx: int = 0, values=None,
):
    row = []
    values = values if values is not None else [None] * 4
    fields = CFG.product_fields[id_name]

    row.append(
        dbc.Col(dbc.Button(
            html.I(className="bi bi-trash3-fill", style={"fontSize": "100%"}),
            size="sm", id={"type": f"delete-{id_name}", "index": idx},
            style={"height": "100%"}, color="secondary", outline=True
        ), width="auto")
    )
    if fields[0]:
        row.append(dbc.Col(dbc.Select(
            options=load_brands(id_name), value=values[0],
            id={"type": f"brand-{id_name}", "index": idx}), width=5))
    if fields[1]:
        row.append(dbc.Col(dbc.Input(
            type="number", id={"type": f"price-{id_name}", "index": idx},
            min=0, value=values[1]
        )))
    if fields[2]:
        row.append(dbc.Col(dbc.Input(
            type="number", id={"type": f"quantity-{id_name}", "index": idx},
            min=0, value=values[2]
        )))
    if fields[3]:
        row.append(dbc.Col(dbc.Input(
            id={"type": f"obs-{id_name}", "index": idx}, value=values[3])))
    return dbc.Row(row, className="g-0", id=f"{id_name}-product-row-{idx}")


def product_form(
    id_name: str
):
    row = []
    style = CENTER | {'width': '100%'}
    row.append(dbc.Col(style={'marginRight': '30px'}, width="auto"))
    fields = CFG.product_fields[id_name]
    label = CFG.product_titles[id_name]

    if fields[0]:
        row.append(dbc.Col(dbc.Label("Marca", style=style), width=5))
    if fields[1]:
        row.append(dbc.Col(dbc.Label("Preço", style=style)))
    if fields[2]:
        row.append(dbc.Col(dbc.Label("Quant.", style=style)))
    if fields[3]:
        row.append(dbc.Col(dbc.Label("Obs.", style=style)))
    return dbc.Row([
        dbc.Col([
            html.Div(DangerouslySetInnerHTML(
                ICONS[id_name]), style={"display": "inline-block"}),
            dbc.Label(
                label, style=BOLD, className="mx-2 mb-0"),
            dbc.Badge("", pill=True, id=f"status-{id_name}"),
        ]),
        dbc.Row(row, className="g-0 mt-2"),
        dbc.Row([
            create_product_form(id_name, idx)
            for idx in range(CFG.product_rows[id_name])
        ], id=f"container-{id_name}", className="g-0"),
        html.Button("+", id=f"add-{id_name}", className="mb-4")
    ], className="m-2 g-0", id=f"{id_name}-heading")
