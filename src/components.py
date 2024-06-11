"""Components for the pages."""

import dash_bootstrap_components as dbc
from dash import html
from typing import Optional
from tools import load_brands


def input_form(
    label: str, id_name: str, input_type: Optional[str] = None,
    placeholder: Optional[str] = None, formtext: Optional[str] = None,
    selection: Optional[list[dict[str, str]]] = None
) -> html.Div:
    elements = []
    elements.append(dbc.Label(label, style={'fontWeight': 'bold'}))

    if input_type:
        elements.append(
            dbc.Input(type=input_type, id=id_name, placeholder=placeholder)
        )
    elif selection:
        elements.append(
            dbc.Select(id=id_name, options=selection)
        )

    if formtext:
        elements.append(dbc.FormText(formtext, color="secondary"))
    return html.Div(elements, className="m-2")


def create_product_form(
    id_name: str, no_price=False, brand=False, price=False,
    no_pattern=False, quantity=False, obs=False, idx: int = 0
):
    row = []
    row.append(
        dbc.Col(dbc.Button(
            "X", outline=True, color="secondary", className="me-1", size="sm",
            id={"type": f"delete-{id_name}", "index": idx}
        ), width="auto")
    )
    if no_price:
        row.append(dbc.Col(dbc.Checkbox(
            id={"type": f"no_price-{id_name}", "index": idx}), width=2))
    if no_pattern:
        row.append(dbc.Col(dbc.Checkbox(
            id={"type": f"no_pattern-{id_name}", "index": idx}), width=2))
    if brand:
        row.append(dbc.Col(dbc.Select(
            options=load_brands(id_name),
            id={"type": f"brand-{id_name}", "index": idx}), width=4))
    if price:
        row.append(dbc.Col(dbc.Input(
            type="number", id={"type": f"price-{id_name}", "index": idx},
            min=0
        )))
    if quantity:
        row.append(dbc.Col(dbc.Input(
            type="number", id={"type": f"quantity-{id_name}", "index": idx},
            min=0
        )))
    if obs:
        row.append(dbc.Col(dbc.Input(
            id={"type": f"obs-{id_name}", "index": idx})))
    return dbc.Row(row, className="g-0", id=f"product-row-{idx}")


def product_form(
    label: str, id_name: str, no_price=False, brand=False, price=False,
    no_pattern=False, quantity=False, obs=False
):
    row = []
    style = {'textAlign': 'center', 'width': '100%'}
    row.append(dbc.Col(style={'marginRight': '30px'}, width="auto"))

    if no_price:
        row.append(dbc.Col(dbc.Label("Faltando", style=style), width=2))
    if no_pattern:
        row.append(dbc.Col(dbc.Label("Fora de padrão", style=style), width=2))
    if brand:
        row.append(dbc.Col(dbc.Label("Marca", style=style), width=4))
    if price:
        row.append(dbc.Col(dbc.Label("Preço", style=style)))
    if quantity:
        row.append(dbc.Col(dbc.Label("Quant.", style=style)))
    if obs:
        row.append(dbc.Col(dbc.Label("Obs.", style=style)))

    return dbc.Row([
        dbc.Col([
            dbc.Label(label, className="mt-4", style={'fontWeight': 'bold'}),
            dbc.Badge("", pill=True, className="mx-2", id=f"status-{id_name}"),
        ]),
        dbc.Row(row, className="g-0"),
        dbc.Row([
            create_product_form(
                id_name, no_price, brand, price, no_pattern, quantity, obs),
        ], id=f"container-{id_name}"),
        html.Button("+", id=f"add-{id_name}")
    ], className="m-2 g-0")


def add_new_form(context: str, idx: int) -> dbc.Row:
    match context:
        case "acucar":
            new_row = create_product_form(
                context, brand=True, price=True,
                no_pattern=True, quantity=True, idx=idx)
        case "arroz":
            new_row = create_product_form(
                context, brand=True, price=True,
                no_pattern=True, quantity=True, idx=idx)
        case "cafe":
            new_row = create_product_form(
                context, brand=True, price=True,
                no_pattern=True, quantity=True, idx=idx)
        case "farinha":
            new_row = create_product_form(
                context, brand=True, price=True,
                no_pattern=True, quantity=True, idx=idx)
        case "feijao":
            new_row = create_product_form(
                context, brand=True, price=True,
                no_pattern=True, quantity=True, idx=idx)
        case "leite":
            new_row = create_product_form(
                context, brand=True, price=True,
                no_pattern=True, quantity=True, idx=idx)
        case "manteiga":
            new_row = create_product_form(
                context, brand=True, price=True,
                no_pattern=True, quantity=True, idx=idx)
        case "soja":
            new_row = create_product_form(
                context, brand=True, price=True,
                no_pattern=True, quantity=True, idx=idx)
        case "banana":
            new_row = create_product_form(
                context, brand=True, price=True, idx=idx)
        case "batata":
            new_row = create_product_form(
                context, price=True, obs=True, idx=idx)
        case "tomate":
            new_row = create_product_form(
                context, price=True, obs=True, idx=idx)
        case "carne":
            new_row = create_product_form(
                context, no_price=True, price=True, obs=True, idx=idx)
        case "pao":
            new_row = create_product_form(
                context, no_price=True, price=True, obs=True, idx=idx)
        case _:
            raise NotImplementedError("No product found")
    return new_row
