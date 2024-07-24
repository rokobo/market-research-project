"""Components for the pages."""

import dash_bootstrap_components as dbc
from dash import html, dcc
from typing import Optional
from tools import load_brands, load_images
from CONFIG import CFG
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML


ICONS = load_images()


def create_product_form(
    id_name: str, brand=False, price=False,
    quantity=False, obs=False, idx: int = 0, values=None
):
    row = []
    values = values if values is not None else [None] * 4

    row.append(
        dbc.Col(dbc.Button(
            "X", outline=True, color="secondary", className="me-1", size="sm",
            id={"type": f"delete-{id_name}", "index": idx}
        ), width="auto")
    )
    if brand:
        row.append(dbc.Col(dbc.Select(
            options=load_brands(id_name), value=values[0],
            id={"type": f"brand-{id_name}", "index": idx}), width=5))
    if price:
        row.append(dbc.Col(dbc.Input(
            type="number", id={"type": f"price-{id_name}", "index": idx},
            min=0, value=values[1]
        )))
    if quantity:
        row.append(dbc.Col(dbc.Input(
            type="number", id={"type": f"quantity-{id_name}", "index": idx},
            min=0, value=values[2]
        )))
    if obs:
        row.append(dbc.Col(dbc.Input(
            id={"type": f"obs-{id_name}", "index": idx}, value=values[3])))
    return dbc.Row(row, className="g-0", id=f"{id_name}-product-row-{idx}")


def product_form(
    label: str, id_name: str, brand=False, price=False,
    quantity=False, obs=False
):
    row = []
    style = {'textAlign': 'center', 'width': '100%'}
    row.append(dbc.Col(style={'marginRight': '30px'}, width="auto"))

    if brand:
        row.append(dbc.Col(dbc.Label("Marca", style=style), width=5))
    if price:
        row.append(dbc.Col(dbc.Label("Preço", style=style)))
    if quantity:
        row.append(dbc.Col(dbc.Label("Quant.", style=style)))
    if obs:
        row.append(dbc.Col(dbc.Label("Obs.", style=style)))
    return dbc.Row([
        dbc.Col([
            html.Div(DangerouslySetInnerHTML(
                ICONS[id_name]), style={"display": "inline-block"}),
            dbc.Label(
                label, style={'fontWeight': 'bold'}, className="mx-2 mb-0"),
            dbc.Badge("", pill=True, id=f"status-{id_name}"),
        ]),
        dbc.Row(row, className="g-0 mt-2"),
        dbc.Row([
            create_product_form(id_name, brand, price, quantity, obs, idx)
            for idx in range(CFG.product_rows[id_name])
        ], id=f"container-{id_name}", className="g-0"),
        html.Button("+", id=f"add-{id_name}", className="mb-4")
    ], className="m-2 g-0", id=f"{id_name}-heading")


def add_new_form(context: str, idx: int, values=None) -> dbc.Row:
    match context:
        case "acucar":
            new_row = create_product_form(
                context, brand=True, price=True,
                quantity=True, idx=idx, values=values)
        case "arroz":
            new_row = create_product_form(
                context, brand=True, price=True,
                quantity=True, idx=idx, values=values)
        case "cafe":
            new_row = create_product_form(
                context, brand=True, price=True,
                quantity=True, idx=idx, values=values)
        case "farinha":
            new_row = create_product_form(
                context, brand=True, price=True,
                quantity=True, idx=idx, values=values)
        case "feijao":
            new_row = create_product_form(
                context, brand=True, price=True,
                quantity=True, idx=idx, values=values)
        case "leite":
            new_row = create_product_form(
                context, brand=True, price=True,
                quantity=True, idx=idx, values=values)
        case "manteiga":
            new_row = create_product_form(
                context, brand=True, price=True,
                quantity=True, idx=idx, values=values)
        case "soja":
            new_row = create_product_form(
                context, brand=True, price=True,
                quantity=True, idx=idx, values=values)
        case "banana":
            new_row = create_product_form(
                context, brand=True, price=True, idx=idx, values=values)
        case "batata":
            new_row = create_product_form(
                context, price=True, obs=True, idx=idx, values=values)
        case "tomate":
            new_row = create_product_form(
                context, price=True, obs=True, idx=idx, values=values)
        case "carne":
            new_row = create_product_form(
                context, price=True,
                obs=True, idx=idx, values=values)
        case "pao":
            new_row = create_product_form(
                context, price=True,
                obs=True, idx=idx, values=values)
        case _:
            raise NotImplementedError("No product found")
    return new_row
