import dash
from dash import html, callback, Input, Output, State, ctx, Patch, ALL, dcc, \
    clientside_callback, ClientsideFunction
from components import product_form, create_product_form
from tools import load_establishments, save_products
from CONFIG import CFG, CLEAR, ICONS, BOLD, CENTER, UNDERLINE, INFO
import dash_bootstrap_components as dbc
import time
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
import dash_mantine_components as dmc

dash.register_page(__name__, path="/")


import dash_ag_grid as dag
layout = html.Div([
    dbc.Navbar([
        dbc.Row([
            html.A(
                DangerouslySetInnerHTML(ICONS[product]),
                id=f"icon-{product}",
                style={"color": "red"}, href=f"#{product}-heading"
            ) for product in CFG.products
        ], className="g-0 m-0 navigation")
    ], className="navbar bg-body", sticky="top", expand=True),
    dbc.Alert([
        html.H4([
            html.I(className="bi bi-info-circle-fill"),
            " Instruções de preenchimento", html.Hr(className="m-1")
        ], className="alert-heading", style=BOLD),
        html.P([
            "Clique tem todos os ícones ",
            html.I(className="bi bi-info-circle"),
            " para saber o funcionamento do site. "
            "Por favor, use preferencialmente o ",
            html.U(html.A(
                ["Chrome ", html.I(className="bi bi-browser-chrome")],
                href="https://www.google.com/chrome/",
                target="_blank",
                style=UNDERLINE | {"color": "inherit"}
            )),
            ", visto que foi testado e "
            "possui compatibilidade plena."
        ], className="mb-0", style={'whiteSpace': 'pre-line'}),
    ], dismissable=False, color="warning"),
    INFO("header-info"),
    dbc.Tooltip(
        "O botão 'Limpar' pode ser usado para começar um relatório do zero. "
        "Você também pode escolher usar o site no modo claro ou noturno, "
        "basta escolher uma opção no seletor à esquerda.",
        target="header-info"),
    html.H1(
        "COLETA DE PREÇOS", className="my-2",
        style=BOLD | CENTER),
    dbc.Stack([
        dmc.SegmentedControl(data=[
            {"value": "light", "label": [
                html.I(className="bi bi-brightness-high-fill"), " Light"]},
            {"value": "dark", "label": [
                "Dark ", html.I(className="bi bi-moon-stars-fill")]}],
            value="light", radius=20, size="sm", id="theme_switch",
            persistence=True, persistence_type="local", transitionDuration=500
        ),
        html.Div(className="mx-auto"),
        CLEAR("confirm-clear", 1),
    ], direction="horizontal", className="mx-2 mb-3 mbt-2"),
    html.Div([
        dbc.Label("Nome do coletor", style=BOLD),
        dbc.Input(type="text", id="collector_name"),
    ], className="m-2"),
    html.Div([
        dbc.Label("Data de coleta", style=BOLD),
        INFO("date-info"),
        dbc.Tooltip(
            "Aperte o botão 'Hoje' para automaticamente preencher "
            "o campo 'Data de coleta'.",
            target="date-info"),
        dbc.InputGroup([
            dbc.Input(type="date", id="collection_date"),
            dbc.Button(
                [html.I(className="bi bi-calendar2-check"), " Hoje"],
                id="fill-date", color="primary")
        ]),
        dbc.FormText(
            "Data em que a coleta foi feita, formato: mm/dd/yyyy",
            color="secondary")
    ], className="m-2"),
    html.Div([
        dbc.Label("Estabelecimento", style=BOLD),
        INFO("estab-info"),
        dbc.Tooltip([
            "Aperte o botão 'Localizar' para preencher o estabelecimento "
            "mais perto da sua localização. ",
            html.Hr(),
            "Abaixo do campo, serão "
            "exibidos as seguintes informações: O endereço do estabelecimento "
            "e os parâmetros da geolocalização (distância até o "
            "estabelecimento, margem de erro da geolocalização e última "
            "atualização da localização)"],
            target="estab-info"),
        dbc.InputGroup([
            dbc.Select(id="establishment", options=load_establishments()),
            dbc.Button(
                [html.I(className="bi bi-geo-alt"), " Localizar"],
                id="fill-establishment", color="primary")
        ]),
        dbc.FormText(
            "...", id="establishment-formtext",
            color="secondary", className="unwrap"),
        html.Hr(className="m-1"),
        dbc.FormText(
            "Geolocalização não usada",
            id="establishment-subformtext", color="secondary")
    ], className="m-2 unwrap"),

    dag.AgGrid(id="ag-grid-1", columnDefs=[
        {
            "field": "Ticker",
            "cellRenderer": "StockLink",
            "editable": False
        },
        {
            "field": "Marca",
            "cellEditor": "agSelectCellEditor",
            "cellEditorParams": {
                "values": ["Apple", "Banana", "Orange"]
            }
        },
        {
            "field": "Quantity",
        },
    ], defaultColDef={"editable": True},
               rowData=[
    {"Marca": "Apple", "Quantity": 10, "Ticker": ""},
    {"Marca": "Banana", "Quantity": 15, "Ticker": ""},
    {"Marca": "Orange", "Quantity": 8, "Ticker": ""},
], dashGridOptions = {"domLayout": "autoHeight", "singleClickEdit": True, "stopEditingWhenCellsLoseFocus": True},
style = {"height": None}),

    html.Div(html.Button(
        html.I(className="bi bi-file-earmark-plus"),
        id=f"add-test", className="mb-4")),

    html.Div([product_form(prd) for prd in CFG.products]),
    html.Div([
        dbc.Label(
            [html.I(className="bi bi-chat-right-text"), " Observações gerais"],
            style=BOLD),
        INFO("obs-info"),
        dbc.Tooltip(
            "Somente anote: Marcas colocadas como Outro/Outra, "
            "observação para administradores do site ou do projeto e "
            "fatos que precisam ser guardados para o futuro.",
            target="obs-info"),
        dbc.Textarea(
            id="general_observations", className="form-control",
            style={'width': '100%', 'height': '150px'},
            placeholder="Algo que tenha ocorrido ou marcas não listadas"),
        dbc.FormText("Opcional: relatar algo relevante", color="secondary")
    ], className="m-2"),
    INFO("save-info"),
    html.Div(dcc.ConfirmDialogProvider(
        html.Div(dbc.Button(
            [html.I(className="bi bi-file-earmark-arrow-up"), " Enviar"],
            color="success", id="save-products"
        ), className="d-grid m-5"),
        id="confirm-send"
    ), id="save-container"),
    dbc.Tooltip(
        "O botão 'Enviar' só poderá ser clicado quando todas as seções "
        "estiverem válidas (ícone e status não podem estar vermelhos). "
        "O botão ficará verde quando o envio estiver liberado.",
        target="save-info"),
    dbc.Modal([
        dbc.ModalHeader(
            dbc.ModalTitle("RELATÓRIO ENVIADO"), close_button=False),
        dbc.ModalBody("Obrigado por enviar seu relatório!"),
        dbc.ModalFooter(
            dbc.Button(
                "Fechar", id="close-send-confirmation", className="ms-auto")),
    ], id="send-confirmed-modal", centered=True, is_open=False),
    html.Div(id="dummy-div-load"),        # save_products  ->  load
    html.Div(id="dummy-div-validation"),  # load           ->  validation
    html.Div(id="dummy-div-progress"),    # validation     ->  progress
    html.Div(id="dummy-div-save"),        # progress       ->  save
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.Stack([
                html.H2("Esperando validação..."),
                dbc.Spinner(color="secondary"),
            ], direction="horizontal", gap=3), close_button=False),
            dbc.ModalBody(html.H6(
                "Se nada acontecer, atualize a página.",
                style=CENTER)),
            dbc.ModalFooter([
                html.H6("Ou limpe o cache:"), CLEAR("confirm-clear", 2)])
        ],
        id="page-loading-modal", is_open=True,
        centered=True, keyboard=False, backdrop="static"),
    dbc.Modal(
        id="geo-loading-modal", is_open=False,
        centered=True, keyboard=False, backdrop="static"),
    dcc.Geolocation(id="geolocation", high_accuracy=True, update_now=True),
    dcc.Interval(id="10-seconds", interval=5*1000),
    html.Div(
        dbc.Stack([
            dbc.Badge("", color="info", id="geolocation-badge"),
            dbc.Badge("", color="success", id="online-badge"),
        ], direction="horizontal"),
        style={"position": "fixed", "bottom": 0, "right": 0, "zIndex": 5}),
])


clientside_callback(
    ClientsideFunction(
        namespace='input',
        function_name='update_badges'
    ),
    Output('online-badge', 'children'),
    Output('online-badge', 'color'),
    Output('geolocation-badge', 'children'),
    Output('geolocation-badge', 'color'),
    Output("geo-loading-modal", "is_open"),
    Output("geo-loading-modal", "children"),
    Output('geo-history', 'data'),
    Input("10-seconds", "n_intervals"),
    State("geolocation", "position"),
    State('geo-history', 'data'),
)
@callback(
    Output("ag-grid-1", "rowTransaction"),
    Input("add-test", "n_clicks"),
)
def a(m):
    return {"add": [{"Marca": None, "Quantity": None}]}

clientside_callback(
    ClientsideFunction(
        namespace='input',
        function_name='fill_date'
    ),
    Output('collection_date', 'value', allow_duplicate=True),
    Input("fill-date", "n_clicks"),
    prevent_initial_call=True
)


clientside_callback(
    ClientsideFunction(
        namespace='input',
        function_name='locate_establishment'
    ),
    Output('establishment', 'value', allow_duplicate=True),
    Output("establishment-subformtext", "children"),
    Input("fill-establishment", "n_clicks"),
    prevent_initial_call=True
)


clientside_callback(
    ClientsideFunction(
        namespace='input',
        function_name='establishment_address'
    ),
    Output("establishment-formtext", "children"),
    Input("establishment", "value"),
    prevent_initial_call=True
)


clientside_callback(
    ClientsideFunction(
        namespace='input',
        function_name='theme_switcher'
    ),
    Output("mantine", "forceColorScheme"),
    Input("theme_switch", "value")
)


clientside_callback(
    ClientsideFunction(
        namespace='input',
        function_name='close_modal'
    ),
    Output("send-confirmed-modal", "is_open", allow_duplicate=True),
    Input("close-send-confirmation", "n_clicks"),
    prevent_initial_call=True
)


clientside_callback(
    ClientsideFunction(
        namespace='input',
        function_name='save_state'
    ),
    Output('store', 'data'),
    Input("dummy-div-save", "className"),
    State("collector_name", "value"),
    State("collection_date", "value"),
    State("establishment", "value"),
    State("general_observations", "value"),
    [State(f"container-{product}", 'children') for product in CFG.products],
    prevent_initial_call=True
)

clientside_callback(
    ClientsideFunction(
        namespace="input",
        function_name="clear_contents"
    ),
    Output('store', 'data', allow_duplicate=True),
    Input({"type": "confirm-clear", "index": ALL}, "submit_n_clicks"),
    prevent_initial_call=True
)


clientside_callback(
    ClientsideFunction(
        namespace="input",
        function_name="display_progress"
    ),
    [Output(f"icon-{product}", 'style') for product in CFG.products],
    Output("save-products", "color"),
    Output("save-container", "className"),
    Output("confirm-send", "message"),
    Output("dummy-div-save", "className"),
    Input("dummy-div-progress", "className"),
    Input("collector_name", "className"),
    Input("collection_date", "className"),
    Input("establishment", "className"),
    [Input(f"status-{product}", 'color') for product in CFG.products],
    [State(f"container-{product}", 'children') for product in CFG.products],
    State("collection_date", "value"),
    prevent_initial_call=True
)


@callback(
    Output("collector_name", "value"),
    Output("collection_date", "value"),
    Output("establishment", "value"),
    Output("general_observations", "value"),
    [Output(f"container-{product}", 'children')
        for product in CFG.products],
    Output("dummy-div-validation", "className"),
    Input("dummy-div-load", "className"),
    Input("confetti", "className"),
    State('store', 'data'),
)
def load_state(_1, _2, data):
    return_data = ["", "", "", ""]
    containers = [[] for _ in range(len(CFG.products))]
    k = len(CFG.fields)

    if data == []:
        for idx, product in enumerate(CFG.products):
            containers[idx].extend([
                create_product_form(product, idx, [None] * k)
                for idx in range(CFG.product_rows[product])
            ])
    else:
        for item in data:
            if "first" in item:
                return_data[:3] = item["first"]
            if "observations" in item:
                return_data[3] = item["observations"]
            if "container" in item:
                idx = CFG.products.index(item["container"])
                containers[idx].append(create_product_form(
                    item["container"], item["row_id"], item["values"]
                ))
    return return_data + containers + [""]


clientside_callback(
    ClientsideFunction(
        namespace='input',
        function_name='delete_product_row'
    ),
    [Output(f"container-{product}", 'children', allow_duplicate=True)
        for product in CFG.products],
    [Input({"type": f"delete-{product}", "index": ALL}, 'n_clicks')
        for product in CFG.products],
    [State(f"container-{product}", 'children') for product in CFG.products],
    prevent_initial_call=True
)


@callback(
    [Output(f"container-{product}", 'children', allow_duplicate=True)
        for product in CFG.products],
    [Input(f"add-{product}", 'n_clicks') for product in CFG.products],
    [State(f"container-{product}", 'children') for product in CFG.products],
    prevent_initial_call=True
)
def add_new_row(*values):
    context = ctx.triggered_id
    if context is None:
        return dash.no_update
    if all(n is None for n in values[:len(CFG.products)]):
        return dash.no_update

    context = context[4:]
    index = CFG.products.index(context)
    new_row = create_product_form(context, int(time.time() * 10))
    patched_children = [dash.no_update] * len(CFG.products)
    patch = Patch()
    patch.append(new_row)
    patched_children[index] = patch
    return patched_children


clientside_callback(
    ClientsideFunction(
        namespace='input',
        function_name='validate_args'
    ),
    [Output({"type": f"{field}-{product}", "index": ALL}, "className")
        for product in CFG.products for field in CFG.fields],
    [Output(f"status-{product}", 'children') for product in CFG.products],
    [Output(f"status-{product}", 'color') for product in CFG.products],
    Output("collector_name", "className"),
    Output("collection_date", "className"),
    Output("establishment", "className"),
    Output("dummy-div-progress", "className"),
    Output("page-loading-modal", "is_open", allow_duplicate=True),
    Input("dummy-div-validation", "className"),
    Input("collector_name", "value"),
    Input("collection_date", "value"),
    Input("establishment", "value"),
    [Input({"type": f"{field}-{product}", "index": ALL}, "value")
        for product in CFG.products for field in CFG.fields],
    [Input(f"container-{product}", 'children')
        for product in CFG.products],
    [State({"type": f"{field}-{product}", "index": ALL}, "value")
        for product in CFG.products for field in CFG.fields],
    State("collector_name", "value"),
    State("collection_date", "value"),
    State("establishment", "value"),
    prevent_initial_call=True
)


@callback(
    Output('store', 'data', allow_duplicate=True),
    Output('geo-history', 'data', allow_duplicate=True),
    Output('dummy-div-load', 'className'),
    Output("send-confirmed-modal", "is_open"),
    Input("confirm-send", "submit_n_clicks"),
    State("collector_name", "value"),
    State("collection_date", "value"),
    State("establishment", "value"),
    State("general_observations", "value"),
    State("geolocation", "position"),
    State('geo-history', 'data'),
    [State({"type": f"{field}-{product}", "index": ALL}, "value")
        for product in CFG.products for field in CFG.fields],
    prevent_initial_call=True
)
def save_args(clicks, name, date, establishment, obs, pos, geo_hist, *values):
    if clicks is None:
        return dash.no_update
    k = len(CFG.fields)
    products = [values[i:i + k] for i in range(0, len(values), k)]
    save_products(products, (name, date, establishment), obs, pos, geo_hist)
    return [], [], "", True
