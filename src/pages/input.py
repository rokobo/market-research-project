import dash
from dash import html, callback, Input, Output, State, ctx, Patch, ALL, dcc, \
    clientside_callback, ClientsideFunction
from components import product_form, add_new_form, ICONS
from tools import load_establishments, save_products
from CONFIG import CFG
import dash_bootstrap_components as dbc
import time
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML

dash.register_page(__name__, path="/")


layout = html.Div([
    dbc.Navbar([
        dbc.Row([
            html.A(
                DangerouslySetInnerHTML(ICONS[product]),
                id=f"icon-{product}",
                style={"color": "red"}, href=f"#{product}-heading"
            ) for product in CFG.products
        ], className="g-0 m-0 navigation")
    ], color="white", sticky="top", expand=True),
    dbc.Alert([
        html.H4(
            "Instruções de preenchimento",
            className="alert-heading", style={'fontWeight': 'bold'}),
        html.P([
            "Só é necessário especificar a Quant. se ela for diferente "
            "da quantidade padrão. \n\n"
            "O envio é liberado se todas as seções estiverem completas. "
            "Caso queira não enviar alguma seção, delete as "
            "fileiras clicando no botão com X.\n\n"
            "Os ícones mostram se as informações de cada seção estão "
            "válidas. Amarelo indica menos items na seção do que o desejado."
            " Clicar no ícone te leva para a seção."
        ], className="mb-0", style={'whiteSpace': 'pre-line'}),
    ], dismissable=True, color="warning"),
    dbc.Stack([
        html.H1(
            "Coleta de preços", className="b-3 mx-auto",
            style={'fontWeight': 'bold', "text-align": "center"}),
        dcc.ConfirmDialogProvider(
            dbc.Button("Limpar", color="warning", id="clear-products"),
            id="confirm-clear",
            message=(
                "Você tem certeza que quer limpar todos os campos? "
                "Essa ação não pode ser revertida! \n\nApós "
                "limpar o cache, atualize a página para aplicar a limpeza."
            )
        )
    ], direction="horizontal"),
    html.Div([
        dbc.Label("Nome do coletor", style={'fontWeight': 'bold'}),
        dbc.Input(type="text", id="collector_name"),
    ], className="m-2"),
    html.Div([
        dbc.Label("Data de coleta", style={'fontWeight': 'bold'}),
        dbc.Input(type="date", id="collection_date"),
        dbc.FormText(
            "Selecione a data do dia em que a coleta foi feita",
            color="secondary")
    ], className="m-2"),
    html.Div([
        dbc.Label("Estabelecimento", style={'fontWeight': 'bold'}),
        dcc.Loading(
            dbc.Stack([
                dbc.Select(id="establishment", options=load_establishments()),
                dbc.Button("Localizar", id="fill-establishment")
            ], direction="horizontal", gap=1),
            overlay_style={"visibility": "visible", "filter": "blur(2px)"}),
        dbc.FormText(
            "...", id="establishment-formtext",
            color="secondary", className="unwrap"),
        html.Hr(className="m-1"),
        dbc.FormText(
            "Geolocalização não usada",
            id="establishment-subformtext", color="secondary")
    ], className="m-2 unwrap"),
    product_form(
        "Açúcar - 1kg", "acucar",
        brand=True, price=True, quantity=True),
    product_form(
        "Arroz - 5kg", "arroz",
        brand=True, price=True, quantity=True),
    product_form(
        "Café - 0.5kg", "cafe",
        brand=True, price=True, quantity=True),
    product_form(
        "Farinha - 1kg", "farinha",
        brand=True, price=True, quantity=True),
    product_form(
        "Feijão - 1kg", "feijao",
        brand=True, price=True, quantity=True),
    product_form(
        "Leite - 1L", "leite",
        brand=True, price=True, quantity=True),
    product_form(
        "Manteiga - 0.2kg", "manteiga",
        brand=True, price=True, quantity=True),
    product_form(
        "Óleo de soja - 0.9L", "soja",
        brand=True, price=True, quantity=True),
    product_form(
        "Banana - 1kg (Nanica e Prata)", "banana",
        brand=True, price=True),
    product_form(
        "Batata - 1kg (mais barata)", "batata",
        price=True, obs=True),
    product_form(
        "Tomate - 1kg (mais barato)", "tomate",
        price=True, obs=True),
    product_form(
        "Carne - 1kg (Coxão Mole)", "carne",
        price=True, obs=True),
    product_form(
        "Pão Francês - 1kg", "pao",
        price=True, obs=True),
    html.Div([
        dbc.Label("Observações gerais", style={'fontWeight': 'bold'}),
        dbc.Textarea(
            id="general_observations", className="form-control",
            style={'width': '100%', 'height': '150px'},
            placeholder="Algo que tenha ocorrido ou marcas não listadas"),
        dbc.FormText("Opcional: relatar algo relevante", color="secondary")
    ], className="m-2"),
    html.Div(dcc.ConfirmDialogProvider(
        html.Div(dbc.Button(
            "Enviar", color="success", id="save-products"
        ), className="d-grid m-5"),
        id="confirm-send"
    ), id="save-container"),
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
                style={"text-align": "center"})),
        ],
        id="page-loading-modal", is_open=True,
        centered=True, keyboard=False, backdrop="static"),
    dcc.Geolocation(id="geolocation", high_accuracy=True, update_now=True),
])


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='locate_establishment'
    ),
    Output('establishment', 'value', allow_duplicate=True),
    Output("establishment-subformtext", "children"),
    Input("fill-establishment", "n_clicks"),
    prevent_initial_call=True
)


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='establishment_address'
    ),
    Output("establishment-formtext", "children"),
    Input("establishment", "value"),
    prevent_initial_call=True
)


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='close_modal'
    ),
    Output("send-confirmed-modal", "is_open", allow_duplicate=True),
    Input("close-send-confirmation", "n_clicks"),
    prevent_initial_call=True
)


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='save_state'
    ),
    Output('store', 'data'),
    Input("dummy-div-save", "className"),
    State('load-flag', 'data'),
    State("collector_name", "value"),
    State("collection_date", "value"),
    State("establishment", "value"),
    State("general_observations", "value"),
    [State(f"container-{product}", 'children') for product in CFG.products],
    prevent_initial_call=True
)

clientside_callback(
    ClientsideFunction(
        namespace="clientside",
        function_name="clear_contents"
    ),
    Output('store', 'data', allow_duplicate=True),
    Input("confirm-clear", "submit_n_clicks"),
    prevent_initial_call=True
)


clientside_callback(
    ClientsideFunction(
        namespace="clientside",
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
    Output('load-flag', 'data'),
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
    return_data = [True, "", "", "", ""]
    containers = [[] for _ in range(len(CFG.products))]

    if data == []:
        for idx, product in enumerate(CFG.products):
            containers[idx].extend([
                add_new_form(product, idx, [None] * 4)
                for idx in range(CFG.product_rows[product])
            ])
    else:
        for item in data:
            if "first" in item:
                return_data[1:4] = item["first"]
            if "observations" in item:
                return_data[4] = item["observations"]
            if "container" in item:
                idx = CFG.products.index(item["container"])
                containers[idx].append(add_new_form(
                    item["container"], item["row_id"], item["values"]
                ))
    return return_data + containers + [""]


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
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
    new_row = add_new_form(context, int(time.time() * 10))
    patched_children = [dash.no_update] * len(CFG.products)
    patch = Patch()
    patch.append(new_row)
    patched_children[index] = patch
    return patched_children


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
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
    Output("page-loading-modal", "is_open"),
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
    Output('dummy-div-load', 'className'),
    Output("send-confirmed-modal", "is_open"),
    Input("confirm-send", "submit_n_clicks"),
    State("collector_name", "value"),
    State("collection_date", "value"),
    State("establishment", "value"),
    State("general_observations", "value"),
    State("geolocation", "position"),
    [State({"type": f"{field}-{product}", "index": ALL}, "value")
        for product in CFG.products for field in CFG.fields],
    prevent_initial_call=True
)
def save_args(clicks, name, date, establishment, obs, pos, *values):
    if clicks is None:
        return dash.no_update
    products = [values[i:i + 4] for i in range(0, len(values), 4)]
    save_products(products, (name, date, establishment), obs)
    return [], "", True
