# flake8: noqa: E501
import dash
from dash import html, callback, Input, Output, State, dcc, \
    clientside_callback, ClientsideFunction
from CONFIG import BOLD
import dash_bootstrap_components as dbc
from os import getenv
import dash_ag_grid as dag
from dotenv import load_dotenv

dash.register_page(__name__)
load_dotenv()


layout = html.Div([
    dbc.Alert([
        html.H5([
            html.I(className="bi bi-info-circle-fill"),
            " Instruções e definições", html.Hr(className="m-1")
        ], className="alert-heading", style=BOLD),
        dcc.Markdown(
            '''
            Só é possível atualizar quando a senha correta está no campo acima. Somente atualize a tabela quando necessário!

            **Data**: Data anotada, Data na hora do envio, Horário na hora do envio.
            **Estab**: Estabelecimento selecionado, distância do local de envio até o estabelecimento seleionado.
            **Loc**: Latidude e Longitude na hora do envio, distância e nome do estabelecimento mais perto na hora do envio.''',
        style={'whiteSpace': 'pre-line'}, className="mb-0")
    ], dismissable=False, color="warning"),
    dbc.Stack([
        html.H1("Relatórios"), html.Div(className="mx-auto"),
        dcc.Loading(dbc.Button(
            "Atualizar dados", id="refresh-files", disabled=True))
    ], direction="horizontal", className="m-2"),
    dbc.Row(
        dbc.Input(
            id="password-report", type="text", debounce=True,
            placeholder="Senha de administrador", persistence=True,
            persistence_type="local"
    ), className="m-2"),
    dbc.Row(
        dag.AgGrid(
            id="ag-grid-files",
            rowData=[{}],
            columnDefs=[
                {'field': 'Data', "maxWidth": 150},
                {'field': 'Nome'},
                {'field': 'Estab'},
                {'field': 'Loc'},
            ],
            columnSize="responsiveSizeToFit",
            defaultColDef={
                "editable": False,
                "sortable": True,
                "resizable": True,
                "wrapText": True,
                "cellStyle": {
                    "padding": 0,
                    "wordBreak": "normal",
                    "lineHeight": "unset"
                },
            },
            dashGridOptions={
                "animateRows": True,
                "domLayout": "autoHeight",
                'headerHeight': 30,
            },
            style={"height": None},
            className="p-0 ag-theme-material",
        ), className="m-2"
    )
], className="mb-20")


clientside_callback(
    ClientsideFunction(
        namespace='report',
        function_name='refresh_files'
    ),
    Output("ag-grid-files", "rowData"),
    Output("files-hash", "data"),
    Output("files-data", "data"),
    Input("refresh-files", "n_clicks"),
    State('refresh-files', 'disabled'),
    State("files-hash", "data"),
    State("files-data", "data"),
    prevent_initial_call=True
)


@callback(
    Output('refresh-files', 'disabled'),
    Input('password-report', 'value'),
)
def unlock_content(password):
    ADM_PASSWORD = getenv("ADM_PASSWORD")
    return not ((password == ADM_PASSWORD) and (ADM_PASSWORD is not None))
