"""Components for the pages."""

import dash_bootstrap_components as dbc
from tools import load_establishments, save_products2
from CONFIG import CFG, BOLD, CENTER, UNDERLINE, COORDINATES
import uuid
from dash import html, callback, Input, Output, State, ALL, dcc, \
    Patch, MATCH, ctx, no_update, ClientsideFunction, clientside_callback
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from itertools import zip_longest
import pandas as pd
import sqlite3 as sql


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


def product_grid2(product):
    headers = []
    fields = CFG.product_fields[product]

    # Headers
    headers.append(dbc.Col(dbc.Button(
        html.I(className="bi bi-trash3"),
        id=f"delete-{product}-header", disabled=True, color="light",
    ), width="auto"))

    if fields[0]:
        headers.append(dbc.Col(dbc.FormText("Marca"), style=CENTER, width=5))
    if fields[1]:
        headers.append(dbc.Col(dbc.FormText("Preço"), style=CENTER))
    if fields[2]:
        headers.append(dbc.Col(dbc.FormText("Qtd"), style=CENTER))

    # Rows
    rows = []
    for _ in range(CFG.product_rows[product]):
        row = []
        unique_id = str(uuid.uuid4())
        row.append(dbc.Col(dbc.Button(
            html.I(className="bi bi-trash3"),
            id={'type': f"delete-{product}", 'index': unique_id},
            outline=True
        ), width="auto"))

        if fields[0]:
            row.append(dbc.Col(dbc.Select(
                id={'type': f"brand-{product}", 'index': unique_id}
            ), width=5))

        if fields[1]:
            row.append(dbc.Col(dbc.Input(
                type="number", debounce=True,
                id={'type': f"price-{product}", 'index': unique_id})))
        if fields[2]:
            row.append(dbc.Col(dbc.Input(
                type="number", debounce=True,
                id={'type': f"quantity-{product}", 'index': unique_id})))
        rows.append(dbc.Row(
            row, className="g-0",
            id={'type': f"row-{product}", 'index': unique_id}))

    return html.Div([
        dbc.Col([
            html.Div(
                html.Img(src=f"assets/icons/{product}.svg"),
                style={"display": "inline-block"}),
            dbc.Label(
                CFG.product_titles[product], style=BOLD, className="mx-2"),
            dbc.Badge("", pill=True, id=f"status-{product}"),
        ], className="p-1 mb-0"),

        dbc.Row(headers),
        dbc.Row(rows, id=f"{product}-rows", className="g-0"),

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


def info_nav(source):
    pages = {
        "": "Home",
        "report": "Relatórios",
        "result": "Resultados",
        "excel": "Excel",
        "paths": "Caminhos"
    }
    return dbc.Row(dbc.Nav([dbc.NavItem(dbc.NavLink(
        name, href=f"/{page}", active=page == source.split(".")[1]
    )) for page, name in pages.items()], pills=True), className="m-2")


def adm_nav(source):
    pages = {
        "": "Home",
        "brands": "Marcas",
    }
    return dbc.Row(dbc.Nav([dbc.NavItem(dbc.NavLink(
        name, href=f"/{page}", active=page == source.split(".")[1]
    )) for page, name in pages.items()], pills=True), className="m-2")


def diagnostics_nav(source):
    pages = {
        "": "Home",
        "local-storage": "Local Storage",
        "icons": "Ícones",
    }
    return dbc.Row(dbc.Nav([dbc.NavItem(dbc.NavLink(
        name, href=f"/{page}", active=page == source.split(".")[1]
    )) for page, name in pages.items()], pills=True), className="m-2")


def create_page(group: str):
    """Create a page for the given group."""
    assert type(group) is str
    assert group in CFG.groups

    group_prds = [
        prd for prd, grp in zip(CFG.products, CFG.groups) if grp == group]
    group_prds.sort()

    layout = html.Div([
        dbc.Navbar([
            dbc.Row([
                html.A(
                    html.Img(
                        src=f"assets/icons/{prd}.svg", id=f"icon-{prd}"),
                    href=f"#{prd}-heading",
                ) for prd in group_prds
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
        dbc.Stack([
            dbc.Button([
                html.I(className="bi bi-house-door-fill", style=BOLD),
                " Home"
            ], color="secondary", href="/", className="m-0"),
            html.Div(className="mx-auto"),
            dbc.DropdownMenu([
                dbc.DropdownMenuItem(
                    grp.capitalize(), href=f"/{grp}",
                    active=group == grp,
                ) for grp in set(CFG.groups) if grp is not None
            ], label="Categoria", color="secondary", class_name="m-0"),
        ], class_name="m-2", direction="horizontal"),
        dbc.Stack([
            html.H2(
                f"Produtos - {group.capitalize()}", className="m-0",
                style=BOLD | CENTER | UNDERLINE),
            dbc.FormText(
                "COLETA DE PREÇOS", style=CENTER, className="m-0"),
        ], direction="vertical"),
        html.Div([
            dbc.Label("Nome do coletor", style=BOLD),
            dbc.Input(
                debounce=True, type="text",
                id=f"collector_name-{group}", persistence=True),
        ], className="m-2"),
        html.Div([
            dbc.Label("Data de coleta", style=BOLD),
            INFO("date-info"),
            dbc.Tooltip(
                "Aperte o botão 'Hoje' para automaticamente preencher "
                "o campo 'Data de coleta'.",
                target="date-info"),
            dbc.InputGroup([
                dbc.Input(
                    debounce=True, type="date", id=f"collection_date-{group}"),
                dbc.Button(
                    [html.I(className="bi bi-calendar2-check"), " Hoje"],
                    id=f"fill-date-{group}", color="primary")
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
                "Abaixo do campo, serão exibidos"
                " as seguintes informações: O endereço do estabelecimento "
                "e os parâmetros da geolocalização (distância até o "
                "estabelecimento, margem de erro da geolocalização e última "
                "atualização da localização)"],
                target="estab-info"),
            dbc.InputGroup([
                dbc.Select(
                    id=f"establishment-{group}",
                    options=load_establishments()),
                dbc.Button(
                    [html.I(className="bi bi-geo-alt"), " Localizar"],
                    id=f"fill-establishment-{group}", color="primary")
            ]),
            dbc.FormText(
                "...", id=f"establishment-formtext-{group}",
                color="secondary", className="unwrap"),
            html.Hr(className="m-1"),
            dbc.FormText(
                "Geolocalização não usada",
                id=f"establishment-subformtext-{group}", color="secondary")
        ], className="m-2 unwrap"),
        html.Div([
            product_grid2(prd) for prd in group_prds], id=f"grids-{group}"),
        dbc.Tooltip([
            "O campo 'Quant.' só precisa ser preenchido quando a quantidade "
            "do produto que você está anotando é diferente da quantidade "
            "especificada na seção. Por exemplo, nesta seção, a quantidade "
            f"padrão é {''.join(map(str, CFG.quantities["acucar"]))}. ",
            html.Hr(),
            "Campos com borda vermelha são obrigatórios e estão com erro: "
            "Campo vazio ou valor errado.",
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
        ], target="section-acucar-info"),
        html.Div([
            dbc.Label([
                html.I(className="bi bi-chat-right-text"),
                " Observações gerais"
            ], style=BOLD),
            INFO("obs-info"),
            dbc.Tooltip(
                "Somente anote: Marcas colocadas como Outro/Outra, "
                "observação para administradores do site ou do projeto e "
                "fatos que precisam ser guardados para o futuro.",
                target="obs-info"),
            dbc.Textarea(
                id=f"general_observations-{group}", className="form-control",
                style={'width': '100%', 'height': '150px'}, persistence=True,
                placeholder="Algo que tenha ocorrido ou marcas não listadas"),
            dbc.FormText("Opcional: relatar algo relevante", color="secondary")
        ], className="m-2"),
        INFO("save-info"),
        html.Div(dcc.ConfirmDialogProvider(
            html.Div(dbc.Button(
                [html.I(className="bi bi-file-earmark-arrow-up"), " Enviar"],
                color="success", id=f"save-products-{group}"
            ), className="d-grid m-5"),
            id=f"confirm-send-{group}"
        ), id=f"save-container-{group}"),
        dbc.Tooltip(
            "O botão 'Enviar' só poderá ser clicado quando todas as seções "
            "estiverem válidas (ícone e status não podem estar vermelhos). "
            "O botão ficará verde quando o envio estiver liberado.",
            target="save-info"),
        dbc.Modal([
            dbc.ModalHeader(
                dbc.ModalTitle("RELATÓRIO ENVIADO"), close_button=False),
            dbc.ModalBody("Obrigado por enviar seu relatório!"),
            dbc.ModalFooter(dbc.Button(
                "Fechar", id=f"close-send-confirmation-{group}",
                className="ms-auto")),
        ], id=f"send-confirmed-modal-{group}", centered=True, is_open=False),
    ])

    for prd in group_prds:
        create_row_callbacks(prd)
        create_validation_callbacks(prd)
    create_save_callback(group, group_prds)

    @callback(
        Output(f"collection_date-{group}", "value"),
        Input(f"fill-date-{group}", "n_clicks"),
        prevent_initial_call=False
    )
    def fill_date(n_clicks):
        return datetime.now().date().isoformat()

    @callback(
        Output(f"establishment-{group}", "value"),
        Output(f"establishment-formtext-{group}", "children"),
        Output(f"establishment-subformtext-{group}", "children"),
        Input(f"fill-establishment-{group}", "n_clicks"),
        Input(f"establishment-{group}", "value"),
        State("geolocation", "position"),
        State("geolocation", "timestamp"),
        prevent_initial_call=False
    )
    def fill_establishment(n_clicks, estab, position, timestamp):
        context = ctx.triggered_id
        if context is not None and context.startswith("establishment-"):
            data = next((
                row for row in COORDINATES if row["display"] == estab), None)
            return estab, data["address"], ""
        if position is None:
            return no_update, "Geolocalização não disponível", no_update
        lat = position["lat"]
        lon = position["lon"]
        accuracy = position["accuracy"]
        smallest_distance = float("inf")
        smallest_data = None
        smallest_estab = None

        for data in COORDINATES:
            dist = haversine(lat, lon, data["latitude"], data["longitude"])
            if dist < smallest_distance:
                smallest_distance = dist
                smallest_data = data
                smallest_estab = data["display"]

        dt = datetime.fromtimestamp(timestamp / 1000)
        formatted = dt.strftime("%Y-%m-%d, %H:%M:%S")
        subtext = f"Distância: {smallest_distance:.2f}km ± {int(accuracy)}m, "
        subtext += f"{formatted}"
        return smallest_estab, smallest_data["address"], subtext
    return layout


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def create_row_callbacks(prd):
    clientside_callback(
        ClientsideFunction(
            namespace='functions',
            function_name='load_brands'
        ),
        Output({'type': f"brand-{prd}", 'index': MATCH}, "options"),
        Input({'type': f"brand-{prd}", 'index': MATCH}, "value"),
        prevent_initial_call=False
    )

    @callback(
        Output(f"{prd}-rows", "children", allow_duplicate=True),
        Input(f"add-{prd}", "n_clicks"),
        prevent_initial_call=True,
    )
    def add_item(button_clicked):
        patched_children = Patch()
        unique_id = str(uuid.uuid4())
        fields = CFG.product_fields[prd]
        row = []

        row.append(dbc.Col(dbc.Button(
            html.I(className="bi bi-trash3"),
            id={'type': f"delete-{prd}", 'index': unique_id},
            outline=True
        ), width="auto"))

        if fields[0]:
            row.append(dbc.Col(dbc.Select(
                id={'type': f"brand-{prd}", 'index': unique_id}), width=5))
        if fields[1]:
            row.append(dbc.Col(dbc.Input(
                type="number",
                id={'type': f"price-{prd}", 'index': unique_id})))
        if fields[2]:
            row.append(dbc.Col(dbc.Input(
                type="number",
                id={'type': f"quantity-{prd}", 'index': unique_id})))
        patched_children.append(dbc.Row(
            row, className="g-0",
            id={'type': f"row-{prd}", 'index': unique_id}))
        return patched_children

    @callback(
        Output(f"{prd}-rows", "children", allow_duplicate=True),
        Input({'type': f"delete-{prd}", 'index': ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def delete_item(n_clicks):
        patched_children = Patch()
        for index, clicks in enumerate(n_clicks):
            if clicks is not None:
                del patched_children[index]
                break
        return patched_children


def create_validation_callbacks(prd):
    clientside_callback(
        ClientsideFunction(
            namespace='functions',
            function_name='validate_rows'
        ),
        Output(f"status-{prd}", "children"),
        Output(f"status-{prd}", "color"),
        Output(f"icon-{prd}", "className"),
        Input({'type': f"delete-{prd}", 'index': ALL}, "className"),
        State(f"icon-{prd}", "src"),
        prevent_initial_call=False
    )

    if CFG.product_fields[prd][0]:
        clientside_callback(
            ClientsideFunction(
                namespace='functions',
                function_name='validate_row_brand'
            ),
            Output({'type': f'brand-{prd}', 'index': MATCH}, "invalid"),
            Output({'type': f'price-{prd}', 'index': MATCH}, "invalid"),
            Output({'type': f'quantity-{prd}', 'index': MATCH}, "invalid"),
            Output({'type': f'delete-{prd}', 'index': MATCH}, "className"),
            Input({'type': f"brand-{prd}", 'index': MATCH}, "value"),
            Input({'type': f"price-{prd}", 'index': MATCH}, "value"),
            Input({'type': f"quantity-{prd}", 'index': MATCH}, "value"),
            State({'type': f"delete-{prd}", 'index': MATCH}, "className"),
            prevent_initial_call=False
        )
    else:
        clientside_callback(
            ClientsideFunction(
                namespace='functions',
                function_name='validate_row_brandless'
            ),
            Output({'type': f'price-{prd}', 'index': MATCH}, "invalid"),
            Output({'type': f'quantity-{prd}', 'index': MATCH}, "invalid"),
            Output({'type': f'delete-{prd}', 'index': MATCH}, "className"),
            Input({'type': f"price-{prd}", 'index': MATCH}, "value"),
            Input({'type': f"quantity-{prd}", 'index': MATCH}, "value"),
            State({'type': f"delete-{prd}", 'index': MATCH}, "className"),
            prevent_initial_call=False
        )


def create_save_callback(group, group_prds):
    clientside_callback(
        ClientsideFunction(
            namespace='functions',
            function_name='validate_sections'
        ),
        Output(f"confirm-send-{group}", "message"),
        Output(f"save-products-{group}", "disabled"),
        Output(f"save-products-{group}", "color"),
        Output(f"save-container-{group}", "className"),
        Input(f"collector_name-{group}", "value"),
        Input(f"collection_date-{group}", "value"),
        Input(f"establishment-{group}", "value"),
        [Input(f"status-{prd}", "color") for prd in group_prds],
        [Input(f"status-{prd}", "children") for prd in group_prds],
        prevent_initial_call=False
    )

    @callback(
        Output(f"grids-{group}", "children"),
        Input(f"confirm-send-{group}", "submit_n_clicks"),
        State(f"collector_name-{group}", "value"),
        State(f"collection_date-{group}", "value"),
        State(f"establishment-{group}", "value"),
        State(f"general_observations-{group}", "value"),
        State("geolocation", "position"),
        State("geolocation", "timestamp"),
        State("geo-history", "data"),
        [
            State({'type': f"brand-{prd}", 'index': ALL}, "value")
            for prd in group_prds],
        [
            State({'type': f"price-{prd}", 'index': ALL}, "value")
            for prd in group_prds],
        [
            State({'type': f"quantity-{prd}", 'index': ALL}, "value")
            for prd in group_prds],
        prevent_initial_call=True
    )
    def save_group_products(
        _clicks, name, date, estab, obs, pos, tm, geo_hist, *args
    ):
        n = len(group_prds)
        brands = args[0:n]
        prices = args[n:2*n]
        qtys = args[2*n:3*n]
        data = []

        for prd, brds, prcs, qtys in zip(group_prds, brands, prices, qtys):
            for brd, prc, qty in zip_longest(brds, prcs, qtys, fillvalue=None):
                if qty is None:
                    qty = CFG.quantities[prd][0]
                data.append({
                    'Produto': prd, 'Marca': brd,
                    'Preço': prc, 'Quantidade': qty
                })

        if pos is None:
            pos_out = [0, 0, 0]
        else:
            pos_out = [pos["lat"], pos["lon"], tm / 1000]
        save_products2(data, (name, date, estab), obs, pos_out, geo_hist)
        return [product_grid2(prd) for prd in group_prds]


def create_database_mod(db):

    @callback(
        Output(f"database-mod-{db}", "children"),
        Input(f"update-db-{db}", "n_clicks"),
        Input(f"select-attribute-{db}", "value"),
    )
    def update_database(n, attr):
        with sql.connect(CFG.config_folder + f"/{db}.db") as database:
            data = pd.read_sql("SELECT * FROM products", database)
        columns = data.columns.to_list()
        attr = attr if attr is not None else "group"
        data = data.to_records(index=False)
        idx = columns.index(attr)
        rows = []
        for row in data:
            formtext = f"Valor atual: {row[idx]}, "
            formtext += f"atualizado em {datetime.now().strftime('%H:%M:%S')}"
            rows.append(dbc.Row([
                dbc.InputGroup([
                    dbc.InputGroupText(row[columns.index("product")]),
                    dbc.Input(
                        debounce=True, type="text", value=row[idx], id={
                            "type": f"input-attribute-{db}",
                            "index": f"{row[0]}-{attr}"
                        }
                    ),
                    dbc.Button("Atualizar", color="secondary", id={
                        "type": f"update-attribute-{db}",
                        "index": f"{row[0]}-{attr}"
                    })
                ], className="p-0"),
                dbc.FormText(formtext, id={
                    "type": f"current-attribute-{db}",
                    "index": f"{row[0]}-{attr}"
                }, color="secondary"),
            ]))
        return html.Div(rows)

    @callback(
        Output(
            {"type": f"current-attribute-{db}", "index": MATCH}, "children"),
        Input({"type": f"update-attribute-{db}", "index": MATCH}, "n_clicks"),
        State({"type": f"input-attribute-{db}", "index": MATCH}, "value"),
        prevent_initial_call=True
    )
    def update_attribute(n, value):
        dtypes = {
            "product": str,
            "quantity": float,
            "quantity_unit": str,
            "product_rows": int,
            "brand_row": int,
            "price_row": int,
            "quantity_row": int,
            "title": str,
            "subtitle": str,
            "split": int,
            "excel_product": str,
            "group": str
        }
        product, attr = ctx.triggered_id["index"].split("-")
        print(value, product, attr)
        with sql.connect(CFG.config_folder + f"/{db}.db") as database:
            data = pd.read_sql("SELECT * FROM products", database)
            database.execute("DROP TABLE IF EXISTS products")
            database.execute("""
                CREATE TABLE products (
                    product TEXT PRIMARY KEY NOT NULL,
                    quantity REAL NOT NULL,
                    quantity_unit TEXT NOT NULL,
                    product_rows INTEGER NOT NULL,
                    brand_row INTEGER NOT NULL,
                    price_row INTEGER NOT NULL,
                    quantity_row INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    subtitle TEXT NOT NULL,
                    split INTEGER NOT NULL,
                    excel_product TEXT NOT NULL,
                    "group" TEXT NOT NULL
                )
            """)
            data.loc[data["product"] == product, attr] = value
            data = data.astype(dtypes)
            data.to_sql("products", database, if_exists="replace", index=False)
        with sql.connect(CFG.config_folder + f"/{db}.db") as database:
            data = pd.read_sql("SELECT * FROM products", database)
        current_val = data.loc[
            data["product"] == product, attr].values[0]
        return f"Valor atual: {current_val}"

    return dbc.Row(id=f"database-mod-{db}", className="m-2")


def navitem_with_icon(name, ref, icon):
    return dbc.NavItem(
        dbc.NavLink([
            html.I(className=f"bi bi-{icon}"),
            " ",
            name
        ], href=f"\\{ref}", active=True, class_name="m-2 bg-dark")
    )
