import dash
from dash import html, callback, Input, Output, State, ALL, dcc, \
    clientside_callback, ClientsideFunction
from components import product_grid, wait_modal, INFO, CLEAR
from tools import load_establishments, save_products
from CONFIG import CFG, ICONS, BOLD, CENTER, UNDERLINE
import dash_bootstrap_components as dbc
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
import dash_mantine_components as dmc

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
        dbc.Input(type="text", id="collector_name", persistence=False),
    ], className="m-2"),
    html.Div([
        dbc.Label("Data de coleta", style=BOLD),
        INFO("date-info"),
        dbc.Tooltip(
            "Aperte o botão 'Hoje' para automaticamente preencher "
            "o campo 'Data de coleta'.",
            target="date-info"),
        dbc.InputGroup([
            dbc.Input(type="date", id="collection_date", persistence=False),
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
            dbc.Select(
                id="establishment", options=load_establishments(),
                persistence=False),
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
    html.Div([product_grid(prd) for prd in CFG.products]),
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
    html.Div([
        wait_modal(modal_info[0], modal_info[1], i) for i, modal_info
        in enumerate([
            ("page-loading-modal", "Validando campos"),
            ("state-loading-modal", "Carregando dados"),
        ])]),
    dbc.Modal(
        id="geo-loading-modal", is_open=False,
        centered=True, keyboard=False, backdrop="static"),
    dcc.Geolocation(id="geolocation", high_accuracy=True, update_now=True),
    dcc.Interval(id="10-seconds", interval=5*1000),
    html.Div(
        dbc.Stack([
            dbc.Badge("", color="primary", id="size-badge"),
            dbc.Badge("", color="secondary", id="geolocation-badge"),
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
    Output("size-badge", "children"),
    Input("10-seconds", "n_intervals"),
    State("geolocation", "position"),
    State('geo-history', 'data'),
)


clientside_callback(
    ClientsideFunction(
        namespace='input',
        function_name='add_row'
    ),
    [
        Output(f"ag-grid-{product}", 'rowTransaction')
        for product in CFG.products
    ],
    [Input(f"add-{product}", 'n_clicks') for product in CFG.products],
    prevent_initial_call=True
)


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
        namespace="input",
        function_name="clear_contents"
    ),
    Output('grid-data', 'data', allow_duplicate=True),
    Output('info-data', 'data', allow_duplicate=True),
    Output("dummy-div-load", "className", allow_duplicate=True),
    Input({"type": "confirm-clear", "index": ALL}, "submit_n_clicks"),
    prevent_initial_call=True
)


clientside_callback(
    ClientsideFunction(
        namespace="input",
        function_name="load_state"
    ),
    [Output(f"ag-grid-{prd}", 'rowData') for prd in CFG.products],
    Output("dummy-div-validation", "className"),
    Output("collector_name", "value"),
    Output("collection_date", "value"),
    Output("establishment", "value"),
    Output("state-loading-modal", "is_open"),
    Input("dummy-div-load", "className"),
    Input("confetti", "className"),
    State('grid-data', 'data'),
    State('info-data', 'data')
)


clientside_callback(
    ClientsideFunction(
        namespace='input',
        function_name='validate_args'
    ),
    [Output(f"status-{prd}", 'children') for prd in CFG.products],
    [Output(f"status-{prd}", 'color') for prd in CFG.products],
    [Output(f"icon-{product}", 'style') for product in CFG.products],
    Output("collector_name", "className"),
    Output("collection_date", "className"),
    Output("establishment", "className"),
    Output("page-loading-modal", "is_open", allow_duplicate=True),
    Output('grid-data', 'data', allow_duplicate=True),
    Output('info-data', 'data', allow_duplicate=True),
    Output("save-products", "color"),
    Output("save-container", "className"),
    Output("confirm-send", "message"),
    Input("dummy-div-validation", "className"),
    Input("collector_name", "value"),
    Input("collection_date", "value"),
    Input("establishment", "value"),
    [Input(f"ag-grid-{prd}", 'cellValueChanged') for prd in CFG.products],
    [Input(f"ag-grid-{prd}", 'virtualRowData') for prd in CFG.products],
    State("collector_name", "value"),
    State("collection_date", "value"),
    State("establishment", "value"),
    prevent_initial_call=True
)


@callback(
    Output('grid-data', 'data', allow_duplicate=True),
    Output('info-data', 'data', allow_duplicate=True),
    Output('geo-history', 'data', allow_duplicate=True),
    Output('dummy-div-load', 'className'),
    Output("send-confirmed-modal", "is_open"),
    Input("confirm-send", "submit_n_clicks"),
    State("collector_name", "value"),
    State("collection_date", "value"),
    State("establishment", "value"),
    State("general_observations", "value"),
    State('geo-history', 'data'),
    State('grid-data', 'data'),
    prevent_initial_call=True
)
def save_args(clicks, name, date, estab, obs, geo_hist, data):
    if clicks is None:
        return dash.no_update
    save_products(data, (name, date, estab), obs, geo_hist[-1], geo_hist)
    return ["reload"], [], [], "", True
