"""Components for the pages."""

import dash_bootstrap_components as dbc
from dash import html
from tools import load_brands
from CONFIG import CFG, ICONS, BOLD, CENTER, INFO
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

    final_row = [dbc.Col([
        html.Div(DangerouslySetInnerHTML(
            ICONS[id_name]), style={"display": "inline-block"}),
        dbc.Label(
            label, style=BOLD, className="mx-2 mb-0"),
        dbc.Badge("", pill=True, id=f"status-{id_name}"),
        (INFO(f"section-{id_name}-info") if id_name == "acucar" else None)
    ])]

    if id_name == "acucar":
        quant = CFG.quantities[id_name]
        final_row += dbc.Tooltip([
            "O campo 'Quant.' só precisa ser preenchido quando a quantidade "
            "do produto que você está anotando é diferente da quantidade "
            "especificada na seção. Por exemplo, nesta seção, a quantidade "
            f"padrão é {quant[0]}{quant[1]}. ",
            html.Hr(),
            "Campos com borda vermelha são obrigatórios",
            html.Hr(),
            "Se não deseja preencher todas as fileiras com itens, clique no "
            "botão com o ícone ", html.I(className="bi bi-trash3-fill"),
            ", para remover a fileira. Caso queira adicionar uma fileira, "
            "clique no botão com o ícone ",
            html.I(className="bi bi-file-earmark-plus"), ".",
            html.Hr(),
            "Status da seção: ",
            "Vermelho -> Campos obrigatórios estão vazios. ",
            "Amarelo -> Campos OK, número de fileiras menor que o esperado. ",
            "Verde -> Campos e número de fileiras OK",
            html.Hr(),
            "O status da seção é espelhado nos ícones do topo da página. "
            "Clicar no ícone de uma seção te leva até ela."
        ], target=f"section-{id_name}-info"),

    final_row.extend([
        dbc.Row(row, className="g-0 mt-2"),
        dbc.Row([
            create_product_form(id_name, idx)
            for idx in range(CFG.product_rows[id_name])
        ], id=f"container-{id_name}", className="g-0"),
        html.Button(
            html.I(className="bi bi-file-earmark-plus"),
            id=f"add-{id_name}", className="mb-4")
    ])
    return dbc.Row(final_row, className="m-2 g-0", id=f"{id_name}-heading")
