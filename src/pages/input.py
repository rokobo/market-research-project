import dash
from dash import html, callback, Input, Output, State, ctx, Patch, ALL
from components import input_form, product_form, add_new_form
from tools import load_establishments, validate_products
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = html.Div([
    html.H1("Coleta de preços"),
    input_form("Nome do coletor", "collector_name", "text"),
    input_form(
        "Data de coleta", "collection_date", "date",
        formtext="Selecione a data do dia em que a coleta foi feita"),
    input_form(
        "Estabelecimento", "establishment",
        formtext="Supermercado por código", selection=load_establishments()),
    dbc.Collapse([
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
    ], id="collection_fields", is_open=False)
])


@callback(
    Output("collection_fields", "is_open"),
    Output("collector_name", "valid"),
    Output("collection_date", "valid"),
    Output("establishment", "valid"),
    Input("collector_name", "value"),
    Input("collection_date", "value"),
    Input("establishment", "value"),
    State("collector_name", "value"),
    State("collection_date", "value"),
    State("establishment", "value")
)
def validade_first_args(_1, _2, _3, *values):
    validations = [(v is not None) and (v != "") for v in values]
    # TODO
    return True, True, True, True
    # return all(validations), *validations


PRODUCTS = [
    "acucar", "arroz", "cafe", "farinha", "feijao", "leite", "manteiga",
    "soja", "banana", "batata", "tomate", "carne", "pao"]


@callback(
    [Output(f"container-{product}", 'children') for product in PRODUCTS],
    [Input(f"add-{product}", 'n_clicks') for product in PRODUCTS],
    [Input({"type": f"delete-{product}", "index": ALL}, 'n_clicks')
        for product in PRODUCTS],
    [State(f"container-{product}", 'children') for product in PRODUCTS]
)
def add_new_row(*values):
    context = ctx.triggered_id
    if context is None:
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
        return patched_children

    # Delete a row
    assert isinstance(context, dict)
    children_states = values[-len(PRODUCTS):]
    idx = context["index"]
    context = context["type"][7:]
    index = PRODUCTS.index(context)

    patched_children = [dash.no_update] * len(PRODUCTS)
    patch = Patch()
    children = children_states[index]
    for i, child in enumerate(children):
        # Find correct row by row index and context index
        if child["props"]["id"][-1] == str(idx):
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
    [Input({"type": f"{field}-{product}", "index": ALL}, "value")
        for product in PRODUCTS for field in FIELDS2 + FIELDS],
    [State({"type": f"{field}-{product}", "index": ALL}, "value")
        for product in PRODUCTS for field in FIELDS2 + FIELDS],
)
def validate_second_args(*values):
    validations = []

    states = values[len(PRODUCTS) * len(FIELDS2 + FIELDS):]
    states = [states[i:i + 6] for i in range(0, len(states), 6)]
    for state in states:
        a = validate_products(state)
        validations.extend(a)

    status1 = []
    status2 = []
    for val in [validations[i:i + 4] for i in range(0, len(validations), 4)]:
        if all(all(v) for v in val):
            status1.append("Correto")
            status2.append("success")
        else:
            status1.append("Faltando")
            status2.append("danger")

    validations = [
        ["correct" if v else "wrong" for v in val] for val in validations]
    return validations + status1 + status2
