"""Components for the pages."""

import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_ag_grid as dag
from tools import load_brands
from CONFIG import CFG, ICONS, BOLD, CENTER
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML

CELL_CLASS = {
    'wrong': 'params.value == null || params.value == ""',
    '': 'params.value != null && params.value != ""'
}


def INFO(comp_id):
    return html.I(className="bi bi-info-circle mx-1 pulse-icon", id=comp_id)


def CLEAR(comp_id, idx):
    return dcc.ConfirmDialogProvider(
        dbc.Button(
            [html.I(className="bi bi-trash3"), " Limpar"],
            color="warning"),
        id={"type": comp_id, "index": idx},
        message=(
            "Você tem certeza que quer limpar todos os campos? "
            "Essa ação não pode ser revertida! \n\nApós "
            "limpar o cache, atualize a página para aplicar a limpeza.")
    )


def product_grid(product):
    fields = CFG.product_fields[product]
    columnDefs = [{
        "cellRenderer": "DeleteRow", "editable": False,
        "suppressSizeToFit": True, "autoHeight": True,
        "width": 45, "cellStyle": {"padding": 2, "margin": 0}
    }]

    if fields[0]:
        columnDefs.append({
            "field": "Marca", "flex": 1.8,
            "cellEditor": "agSelectCellEditor",
            "cellEditorParams": {
                "values": [v["label"] for v in load_brands(product) if "disabled" not in v]
            },
            'cellClassRules': CELL_CLASS
        })
    if fields[1]:
        columnDefs.append({
            "field": "Preço",  "flex": 1,
            'cellDataType': 'number', 'cellEditor': 'agNumberCellEditor',
            'cellEditorParams': {'min': 0.001, 'precision': 3},
            'cellClassRules': CELL_CLASS
        })
    if fields[2]:
        columnDefs.append({
            "field": "Quant", "flex": 1, "headerName": "Quant.",
            'cellDataType': 'number', 'cellEditor': 'agNumberCellEditor',
            'cellEditorParams': {'min': 0.001, 'precision': 3},
        })

    return dbc.Row([
        dbc.Col([
            html.Div(DangerouslySetInnerHTML(
                ICONS[product]), style={"display": "inline-block"}),
            dbc.Label(
                CFG.product_titles[product], style=BOLD, className="mx-2 mb-0"),
            dbc.Badge("", pill=True, id=f"status-{product}"),
            (INFO(f"section-{product}-info") if product == "acucar" else None)
        ], className="p-1"),
        dag.AgGrid(
            id=f"ag-grid-{product}",
            columnDefs=columnDefs,
            defaultColDef={
                "editable": True,
                "sortable": False,
                "resizable": False,
                "suppressMovable": True,
                "cellStyle": {"paddingLeft": 3},
            },
            rowData=[{}] * CFG.product_rows[product],
            dashGridOptions={
                "domLayout": "autoHeight",
                "singleClickEdit": True,
                "stopEditingWhenCellsLoseFocus": True,
                "noRowsOverlayComponent": "CustomNoRowsOverlay",
                'headerHeight': 20
            },
            style={"height": None},
            className="p-0 ag-theme-material",
        ),
        dbc.Button(
            html.I(className="bi bi-file-earmark-arrow-down"),
            id=f"add-{product}", outline=True, color="secondary"),
    ], className="mx-2 mt-4")


def wait_modal(id, source, index):
    return dbc.Modal([
        dbc.ModalHeader(dbc.Stack([
            dbc.Stack([
                html.H2("Esperando validação..."),
                dbc.Spinner(color="secondary")
            ], direction="horizontal", gap=3),
            html.Small(f"Fonte: {source}")
        ]), close_button=False),
        dbc.ModalBody(
            html.H6("Se nada acontecer, atualize a página.", style=CENTER)),
        dbc.ModalFooter([
            html.H6("Ou limpe o cache:"), CLEAR("confirm-clear", index)])
    ], id=id, is_open=True, centered=True, keyboard=False, backdrop="static")
