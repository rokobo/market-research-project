import dash
from dash import html, callback, Input, Output, State, ctx, Patch, ALL, dcc, \
    clientside_callback, ClientsideFunction
from components import input_form, product_form, add_new_form
from tools import load_establishments, save_products
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")

layout = html.Div([
    dbc.Alert([
            html.H4(
                "Instruções de preenchimento",
                className="alert-heading", style={'fontWeight': 'bold'}),
            html.P([
                "Se a quant. coletada não for igual a quant. padrão, "
                "especifique a quant. coletada com a mesma unidade de medida "
                "do título da seção. \n\n"
                "O envio é liberado se todas as seções estiverem completas. "
                "Caso queira não enviar alguma seção, delete a "
                "fileira clicando no botão com X."
            ], className="mb-0", style={'whiteSpace': 'pre-line'}),
    ], dismissable=True, color="warning"),
    html.H1("Coleta de preços", className="m-3", style={'fontWeight': 'bold'}),
    input_form("Nome do coletor", "collector_name", "text"),
    input_form(
        "Data de coleta", "collection_date", "date",
        formtext="Selecione a data do dia em que a coleta foi feita"),
    input_form(
        "Estabelecimento", "establishment",
        formtext="Supermercado por código", selection=load_establishments()),
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
        "Banana - 1kg (anotar Nanica e Prata)", "banana",
        brand=True, price=True),
    product_form(
        "Batata - 1kg (anotar a mais barata)", "batata",
        price=True, obs=True),
    product_form(
        "Tomate - 1kg (anotar o mais barato)", "tomate",
        price=True, obs=True),
    product_form(
        "Carne - 1kg (Coxão Mole)", "carne",
        price=True, obs=True),
    product_form(
        "Pão Francês - 1kg", "pao",
        price=True, obs=True),
    input_form(
        "Observações gerais",
        "general_observations", "textarea",
        "Algo que tenha ocorrido ou marcas não listadas",
        "Opcional: relatar algo relevante"
    ),
    html.Div(dbc.Button(
        "Enviar", color="success", id="save-products"
    ), className="d-grid m-5"),
    dcc.Interval(id="save-interval", interval=2 * 1000),
    html.Div(id="dummy-div-validation"),  # For calling validation after load
    html.Div(id="dummy-div-save"),  # For calling save after load
    html.Div(id="dummy-div-load")  # For calling load after save products
])

PRODUCTS = [
    "acucar", "arroz", "cafe", "farinha", "feijao", "leite", "manteiga",
    "soja", "banana", "batata", "tomate", "carne", "pao"]


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='save_state'
    ),
    Output('store', 'data'),
    Input("save-interval", "n_intervals"),
    Input("dummy-div-save", "className"),
    State('load-flag', 'data'),
    State("collector_name", "value"),
    State("collection_date", "value"),
    State("establishment", "value"),
    State("general_observations", "value"),
    [State(f"container-{product}", 'children') for product in PRODUCTS],
    prevent_initial_call=True
)


@callback(
    Output('load-flag', 'data'),
    Output("collector_name", "value"),
    Output("collection_date", "value"),
    Output("establishment", "value"),
    Output("general_observations", "value"),
    [Output(f"container-{product}", 'children', allow_duplicate=True)
        for product in PRODUCTS],
    Output("dummy-div-validation", "className"),
    Output("dummy-div-save", "className"),
    Input("save-products", 'children'),
    Input("dummy-div-load", 'className'),
    State('store', 'data'),
    prevent_initial_call=True
)
def load_state(_1, _2, data):
    if data is None:
        return dash.no_update

    return_data = []
    return_data.append(True)
    containers = [[] for _ in range(len(PRODUCTS))]

    if data == []:
        return_data.extend([None]*4)
        for idx, product in zip(range(len(PRODUCTS)), PRODUCTS):
            containers[idx].append(add_new_form(
                product, 0, [None] * 4
            ))
        return return_data + containers + ["", ""]

    for item in data:
        if "first" in item:
            return_data.extend(item["first"])
        if "observations" in item:
            return_data.append(item["observations"])
        if "container" in item:
            idx = PRODUCTS.index(item["container"])
            containers[idx].append(add_new_form(
                item["container"], item["row_id"], item["values"]
            ))
    return return_data + containers + ["", ""]


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='delete_product_row'
    ),
    [Output(f"container-{product}", 'children', allow_duplicate=True)
        for product in PRODUCTS],
    [Input({"type": f"delete-{product}", "index": ALL}, 'n_clicks')
        for product in PRODUCTS],
    [State(f"container-{product}", 'children') for product in PRODUCTS],
    prevent_initial_call=True
)


@callback(
    [Output(f"container-{product}", 'children', allow_duplicate=True)
        for product in PRODUCTS],
    [Input(f"add-{product}", 'n_clicks') for product in PRODUCTS],
    [State(f"container-{product}", 'children') for product in PRODUCTS],
    prevent_initial_call=True
)
def add_new_row(*values):
    context = ctx.triggered_id
    if context is None:
        return dash.no_update
    if all(n is None for n in values[:len(PRODUCTS)]):
        return dash.no_update

    context = context[4:]
    index = PRODUCTS.index(context)
    idx = values[index]
    new_row = add_new_form(context, idx)
    patched_children = [dash.no_update] * len(PRODUCTS)
    patch = Patch()
    patch.append(new_row)
    patched_children[index] = patch
    return patched_children


FIELDS = ["brand", "price", "quantity", "obs"]


clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='validate_args_1'
    ),
    Output("collector_name", "className"),
    Output("collection_date", "className"),
    Output("establishment", "className"),
    Input("collector_name", "value"),
    Input("collection_date", "value"),
    Input("establishment", "value"),
    State("collector_name", "value"),
    State("collection_date", "value"),
    State("establishment", "value")
)

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='validate_args_2'
    ),
    [Output({"type": f"{field}-{product}", "index": ALL}, "className")
        for product in PRODUCTS for field in FIELDS],
    [Output(f"status-{product}", 'children') for product in PRODUCTS],
    [Output(f"status-{product}", 'color') for product in PRODUCTS],
    Output("save-products", "disabled"),
    Output("save-products", "color"),
    Input("dummy-div-validation", "className"),
    [Input({"type": f"{field}-{product}", "index": ALL}, "value")
        for product in PRODUCTS for field in FIELDS],
    [Input(f"container-{product}", 'children')
        for product in PRODUCTS],
    [State({"type": f"{field}-{product}", "index": ALL}, "value")
        for product in PRODUCTS for field in FIELDS]
)


@callback(
    Output('store', 'data', allow_duplicate=True),
    Output('dummy-div-load', 'className'),
    Input("save-products", "n_clicks"),
    State("collector_name", "value"),
    State("collection_date", "value"),
    State("establishment", "value"),
    State("general_observations", "value"),
    [State({"type": f"{field}-{product}", "index": ALL}, "value")
        for product in PRODUCTS for field in FIELDS],
    prevent_initial_call=True
)
def save_args(clicks, name, date, establishment, obs, *values):
    if clicks is None:
        return dash.no_update
    products = [values[i:i + 4] for i in range(0, len(values), 4)]
    save_products(products, (name, date, establishment))
    return [], ""
