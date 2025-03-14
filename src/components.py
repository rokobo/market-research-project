"""Components for the pages."""

import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_ag_grid as dag
from tools import load_brands
from CONFIG import CFG, ICONS, BOLD, CENTER
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML


def INFO(comp_id):
    return html.I(className="bi bi-info-circle mx-1 pulse-icon", id=comp_id)


def CLEAR(comp_id, idx):
    return dcc.ConfirmDialogProvider(
        dbc.Button(
            [html.I(className="bi bi-trash3"), " Limpar"],
            color="warning"),
        id={"type": comp_id, "index": idx},
        message=(
            "Você tem certeza que quer limpar todos os campos?\n\n"
            "Essa ação não pode ser revertida!")
    )


CELL_CLASS = {
    'wrong': 'params.value == null || params.value == ""',
    'correct': 'params.value != null && params.value != ""'
}


def product_grid(product):
    fields = CFG.product_fields[product]
    columnDefs = [{
        "cellRenderer": "DeleteRenderer", "editable": False, "maxWidth": 40,
        "cellClass": "delete-cell", 'field': "delete", "headerName": "",
    }]

    if fields[0]:
        columnDefs.append({
            "field": "Marca", 'cellDataType': 'text', "flex": 2,
            "cellRenderer": "SelectRenderer", "editable": False,
            "cellRendererParams": {"options": load_brands(product)},
            "cellStyle": {"paddingLeft": 0, "margin": 0},
            'cellClassRules': CELL_CLASS
        })
    if fields[1]:
        columnDefs.append({
            "field": "Preço", 'cellClass': "form-control", "flex": 1,
            'cellDataType': 'number', 'cellEditor': 'agNumberCellEditor',
            'cellEditorParams': {'min': 0.001, 'precision': 3},
            'cellClassRules': CELL_CLASS
        })
    if fields[2]:
        columnDefs.append({
            "field": "Quantidade",
            'cellDataType': 'number', 'cellEditor': 'agNumberCellEditor',
            'cellEditorParams': {'min': 0.001, 'precision': 3},
            'cellClass': "correct form-control", "flex": 1
        })

    return html.Div([
        dbc.Col([
            html.Div(DangerouslySetInnerHTML(
                ICONS[product]), style={"display": "inline-block"}),
            dbc.Label(
                CFG.product_titles[product], style=BOLD, className="mx-2"),
            dbc.Badge("", pill=True, id=f"status-{product}"),
            (INFO(f"section-{product}-info") if product == "acucar" else None)
        ], className="p-1 mb-0"),
        dag.AgGrid(
            id=f"ag-grid-{product}",
            columnDefs=columnDefs,
            defaultColDef={
                "editable": True,
                "sortable": False,
                "resizable": False,
                "suppressMovable": True,
                "cellStyle": {"padding": 0, "paddingLeft": 5},
            },
            rowData=[{}] * CFG.product_rows[product],
            columnSize="autoSize", columnSizeOptions={"keys": ["delete"]},
            dashGridOptions={
                "animateRows": False,
                "domLayout": "autoHeight",
                "singleClickEdit": True,
                "stopEditingWhenCellsLoseFocus": True,
                'stopEditingWhenGridLosesFocus': True,
                "noRowsOverlayComponent": "NoRowsOverlay",
                'headerHeight': 20,
                'reactiveCustomComponents': True
            },
            style={"height": None},
            className="p-0 ag-theme-material",
        ),
        html.Div(dbc.Button(
            html.I(className="bi bi-file-earmark-arrow-down"),
            id=f"add-{product}", outline=True, color="secondary"
        ), className="d-grid gap-2")
    ], className="mx-2 mt-4", id=f"{product}-heading", role="product-div")


def wait_modal(id, source, index):
    return dbc.Modal([
        dbc.ModalHeader(dbc.Stack([
            dbc.Stack([
                html.H2("Carregando site..."),
                dbc.Spinner(color="secondary")
            ], direction="horizontal", gap=3),
            html.Small(f"Etapa: {source}")
        ]), close_button=False),
        dbc.ModalBody(
            html.H6("Se nada acontecer, atualize a página.", style=CENTER)),
        dbc.ModalFooter([
            html.H6("Ou limpe o cache:"), CLEAR("confirm-clear", index)])
    ], id=id, is_open=True, centered=True, keyboard=False, backdrop="static")


def adm_nav(source):
    pages = {
        "report": "Relatórios", "result": "Resultados", "excel": "Excel",
        "paths": "Caminhos"
    }
    return dbc.Row(dbc.Nav([dbc.NavItem(dbc.NavLink(
        name, href=f"/{page}", active=page == source.split(".")[1]
    )) for page, name in pages.items()], pills=True), className="m-2")
