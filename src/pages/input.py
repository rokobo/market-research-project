import dash
from dash import html, callback, Input, Output, State, ctx, Patch, ALL, dcc
from components import input_form, product_form, add_new_form
from tools import load_establishments, validate_products, save_products
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = html.Div([
    dbc.Alert([
            html.H4(
                "Instruções de preenchimento",
                className="alert-heading", style={'fontWeight': 'bold'}),
            html.P([
                "Se a quantidade coletada não for igual à quantidade padrão, "
                "selecione \"Fora de padrão\" e especifique a quantidade "
                "coletada com a mesma unidade de medida especificada na seção"
            ], className="mb-0"),
    ], dismissable=True, color="warning"),
    html.H1("Coleta de preços", className="m-3"),
    input_form("Nome do coletor", "collector_name", "text"),
    input_form(
        "Data de coleta", "collection_date", "date",
        formtext="Selecione a data do dia em que a coleta foi feita"),
    input_form(
        "Estabelecimento", "establishment",
        formtext="Supermercado por código", selection=load_establishments()),
    product_form(
        "Açúcar - 1kg", "acucar",
        brand=True, price=True, no_pattern=True, quantity=True),
    product_form(
        "Arroz - 5kg", "arroz",
        brand=True, price=True, no_pattern=True, quantity=True),
    product_form(
        "Café - 0.5kg", "cafe",
        brand=True, price=True, no_pattern=True, quantity=True),
    product_form(
        "Farinha - 1kg", "farinha",
        brand=True, price=True, no_pattern=True, quantity=True),
    product_form(
        "Feijão - 1kg", "feijao",
        brand=True, price=True, no_pattern=True, quantity=True),
    product_form(
        "Leite - 1L", "leite",
        brand=True, price=True, no_pattern=True, quantity=True),
    product_form(
        "Manteiga - 0.2kg", "manteiga",
        brand=True, price=True, no_pattern=True, quantity=True),
    product_form(
        "Óleo de soja - 0.9L", "soja",
        brand=True, price=True, no_pattern=True, quantity=True),
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
        no_price=True, price=True, obs=True),
    product_form(
        "Pão Francês - 1kg", "pao",
        no_price=True, price=True, obs=True),
    input_form(
        "Observações gerais",
        "general_observations", "textarea",
        "Algo que tenha ocorrido ou marcas não listadas",
        "Opcional: relatar algo relevante"
    ),
    html.Div(dbc.Button(
        "Salvar", color="success", id="save-products"
    ), className="d-grid m-5"),
    dcc.Interval(id="save-interval", interval=2 * 1000),
    html.Div(id="dummy-div-validation"),  # For calling validation after load
    html.Div(id="dummy-div-save")  # For calling save after load
])

PRODUCTS = [
    "acucar", "arroz", "cafe", "farinha", "feijao", "leite", "manteiga",
    "soja", "banana", "batata", "tomate", "carne", "pao"]


@callback(
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
def save_state(
    _1, _2, load_flag, name, date, establishment, observations, *products
):
    if load_flag is None:
        return dash.no_update

    data = []
    data.append({
        'first': [name, date, establishment]
    })
    data.append({'observations': observations})

    for product, product_name in zip(products, PRODUCTS):
        if len(product) == 0:
            data.append({
                "container": product_name, "values": [None] * 6,
                "row_id": f"{product_name}-product-row-0"
            })
            continue
        for row in product:
            row_id = row["props"]["id"]
            val = row["props"]["children"]
            vals = {}

            for idx in range(len(val)):
                try:
                    value = val[idx]["props"]["children"]["props"]["value"]
                    vals[idx] = value
                except Exception:
                    pass
            match len(val):
                case 5:
                    values = [None, vals[1], vals[2], vals[3], vals[4], None]
                case 4:
                    values = [vals[1], None, None, vals[2], None, vals[3]]
                case 3:
                    if isinstance(vals[1], str):
                        values = [None, None, vals[1], vals[2], None, None]
                    else:
                        values = [None, None, None, vals[1], None, vals[2]]
                case _:
                    values = [None] * 6
            data.append({
                "container": product_name, "values": values,
                "row_id": row_id.split("-")[-1]
            })
    return data


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
    State('store', 'data'),
    prevent_initial_call=True
)
def load_state(_, data):
    if data is None:
        return dash.no_update

    return_data = []
    return_data.append(True)
    containers = [[] for _ in range(len(PRODUCTS))]

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


@callback(
    [
        Output(f"container-{product}", 'children', allow_duplicate=True)
        for product in PRODUCTS],
    [Input(f"add-{product}", 'n_clicks') for product in PRODUCTS],
    [Input({"type": f"delete-{product}", "index": ALL}, 'n_clicks')
        for product in PRODUCTS],
    [State(f"container-{product}", 'children') for product in PRODUCTS],
    prevent_initial_call=True
)
def add_new_row(*values):
    context = ctx.triggered_id
    if context is None:
        return dash.no_update
    if all(n is None for n in values[:len(PRODUCTS)]):
        return dash.no_update

    # Add a new row
    if isinstance(context, str):
        context = context[4:]
        index = PRODUCTS.index(context)
        idx = values[index]

        new_row = add_new_form(context, idx)

        patched_children = [dash.no_update] * len(PRODUCTS)
        patch = Patch()
        patch.append(new_row)
        patched_children[index] = patch
    elif isinstance(context, dict):  # Delete a row
        children_states = values[-len(PRODUCTS):]
        idx = context["index"]
        context = context["type"][7:]
        index = PRODUCTS.index(context)

        patched_children = [dash.no_update] * len(PRODUCTS)
        patch = Patch()
        children = children_states[index]
        for i, child in enumerate(children):
            # Find correct row by row index and context index
            if child["props"]["id"] == f"{context}-product-row-{idx}":
                del patch[i]
                break
        patched_children[index] = patch
    return patched_children


FIELDS = ["brand", "price", "quantity", "obs"]
FIELDS2 = ["no_pattern", "no_price"]


@callback(
    [Output({"type": f"{field}-{product}", "index": ALL}, "className")
        for product in PRODUCTS for field in FIELDS],
    [Output(f"status-{product}", 'children') for product in PRODUCTS],
    [Output(f"status-{product}", 'color') for product in PRODUCTS],
    Output("collector_name", "className"),
    Output("collection_date", "className"),
    Output("establishment", "className"),
    Output("save-products", "disabled"),
    Output("save-products", "color"),
    Input("dummy-div-validation", "className"),
    [Input({"type": f"{field}-{product}", "index": ALL}, "value")
        for product in PRODUCTS for field in FIELDS2 + FIELDS],
    Input("save-products", "n_clicks"),
    Input("collector_name", "value"),
    Input("collection_date", "value"),
    Input("establishment", "value"),
    [State({"type": f"{field}-{product}", "index": ALL}, "value")
        for product in PRODUCTS for field in FIELDS2 + FIELDS],
    State("collector_name", "value"),
    State("collection_date", "value"),
    State("establishment", "value"),
    State("general_observations", "value")
)
def validate_args(_, *values):
    validations = []
    context = ctx.triggered_id

    input_size = len(PRODUCTS) * len(FIELDS2 + FIELDS)

    # Validate products
    states = values[-input_size - 4:-4]
    states = [states[i:i + 6] for i in range(0, len(states), 6)]
    for state in states:
        a = validate_products(state)
        validations.extend(a)

    # Change border based on validation
    status1 = []
    status2 = []
    for val in [validations[i:i + 4] for i in range(0, len(validations), 4)]:
        if all(all(v) for v in val):
            status1.append("Correto")
            status2.append("success")
        else:
            status1.append("Erro")
            status2.append("danger")

    # Change border based on validation
    validations = [
        ["correct" if v else "wrong" for v in val] for val in validations]

    validations2 = [
        "correct" if (v is not None) and (v != "")
        else "wrong" for v in values[input_size+1:input_size+4]]

    validated_return = validations + status1 + status2 + validations2
    unvalidated_return = validated_return + [True, "danger"]
    validated_return += [False, "success"]

    # Guard clauses for saving info
    if not all(val in ["correct", []] for val in validations2):
        return unvalidated_return

    if not all(i in ["correct", []] for val in validations for i in val):
        return unvalidated_return

    if context != "save-products":
        return validated_return

    # Save products
    save_products(states, values[-4:])
    return validated_return
