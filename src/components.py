"""Components for the pages."""

import dash_bootstrap_components as dbc
from dash import html
from typing import Optional
from tools import load_brands


ICONS = {
    "acucar": "cubes", "arroz": "bowl-rice", "cafe": "mug-hot",
    "farinha": "wheat-awn", "feijao": "seedling", "leite": "bottle-droplet",
    "manteiga": "cube", "soja": "wine-bottle", "banana": "phone",
    "batata": "bacterium", "tomate": "apple-whole",
    "carne": "drumstick-bite", "pao": "bread-slice"}


def input_form(
    label: str, id_name: str, input_type: Optional[str] = None,
    placeholder: Optional[str] = None, formtext: Optional[str] = None,
    selection: Optional[list[dict[str, str]]] = None
) -> html.Div:
    elements = []
    elements.append(dbc.Label(label, style={'fontWeight': 'bold'}))

    if input_type:
        if input_type == "date":
            elements.append(
                dbc.Input(
                    type=input_type, id=id_name, placeholder=placeholder
                )
            )
        elif input_type == "textarea":
            elements.append(
                dbc.Textarea(
                    placeholder=placeholder, id=id_name,
                )
            )
        else:
            elements.append(
                dbc.Input(
                    type=input_type, id=id_name, placeholder=placeholder
                )
            )
    elif selection:
        elements.append(
            dbc.Select(id=id_name, options=selection)
        )

    if formtext:
        elements.append(dbc.FormText(formtext, color="secondary"))
    return html.Div(elements, className="m-2", id=f"input-form-{id_name}")


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
            html.I(className=f"fa-solid fa-{ICONS[id_name]}"),
            dbc.Label(
                label, style={'fontWeight': 'bold'}, className="mx-2"),
            dbc.Badge("", pill=True, id=f"status-{id_name}"),
        ]),
        dbc.Row(row, className="g-0"),
        dbc.Row([
            create_product_form(
                id_name, brand, price, quantity, obs),
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
