# flake8: noqa: E501
import dash
from dash import html, callback, Input, Output, State, dcc, \
    clientside_callback, ClientsideFunction, MATCH, ctx, ALL
import pandas as pd
from CONFIG import BOLD, CFG, COORDINATES
from tools import delete_old_reports, haversine
import dash_bootstrap_components as dbc
from os import getenv, listdir
from os.path import join
import dash_ag_grid as dag
from dotenv import load_dotenv
from components import adm_nav
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import localtime, strftime


dash.register_page(__name__)
load_dotenv()


def get_report_months():
    now = datetime.now()
    current_date = datetime(now.year, now.month, 1)
    dates = [
        (current_date - relativedelta(months=i)
        ).strftime("%Y-%m") for i in range(CFG.report_timeout_months, -1, -1)]
    return dates[::-1]


def update_reports_list():
    delete_old_reports()
    items = []
    files = listdir(CFG.data)
    files = sorted(files, reverse=True)
    for idx, file in enumerate(files):
        parts = file.split("|")
        parts[-1] = parts[-1].replace(".csv", "")
        target = COORDINATES[parts[3]]
        distance = haversine(parts[4], parts[5], target["Latitude"], target["Longitude"])
        items.append(dbc.Button(
            dbc.Collapse(id={"type": "file-collapse", "index": idx},
                children=dbc.Row([
                    dbc.Col([
                        html.P(parts[0], style={"font-size": "0.8em"}),
                        html.P(strftime(
                            "%Y-%m-%d %H:%M:%S",
                            localtime(int(parts[1]))
                        ), style={"font-size": "0.8em"} | BOLD)
                    ]),
                    dbc.Col([
                        html.P(parts[2], style={"font-size": "0.8em"}),
                        html.P(
                            f"{int(distance)} metros",
                            style={"font-size": "0.8em"})
                    ]),
                    dbc.Col(html.P(parts[3], style={"font-size": "0.8em"})),
                    dbc.Modal(
                        id={"type": "file-modal", "index": idx}, size="lg"),
                ]), className="p-0"),
            id={"type": "file-button", "index": idx},
            color=None,
        ))
        items.append(html.Hr(className="mx-10"))
    return items


layout = html.Div([
    adm_nav(__name__),
    dbc.Alert([
        html.H5([
            html.I(className="bi bi-info-circle-fill"),
            " Instruções e definições", html.Hr(className="m-1")
        ], className="alert-heading", style=BOLD),
        dcc.Markdown(
            '''
            Só é possível ver os relatórios quando a senha correta está no campo abaixo. Somente use quando necessário! Clique para abrir o relatório.

            **Data**: Data anotada, Data na hora do envio, Horário na hora do envio.
            **Loc/Nome**: Distância do estabelecimento na hora do envio e nome do coletor.
            **Estab**: Estabelecimento selecionado.''',
        style={'whiteSpace': 'pre-line'}, className="mb-0")
    ], dismissable=False, color="warning"),
    dbc.Stack([
        html.H1("Relatórios"), html.Div(className="mx-auto"),
        dbc.Button("Atualizar", id="update-files-button")
    ], direction="horizontal", className="m-2"),
    dbc.Row([
        dbc.Input(
            id="password-report", type="text", debounce=True,
            placeholder="Senha de administrador", persistence=True,
            persistence_type="local"),
        dbc.InputGroup([dbc.Select(
            id='filter-report-date', value="Todos",
            options=[{"label": "Todos", "value": "Todos"}] + [{
                "label": dt, "value": dt
            } for dt in get_report_months()]
        ), dbc.InputGroupText("Data")], className="p-0"),
        dbc.InputGroup([dbc.Select(
            id='filter-report-estab', value="Todos",
            options=[
                {"label": "Todos", "value": "Todos"},
                {"label": "Sem estabelecimento", "value": "Sem"}
            ] + [{
                "label": est.split(" ")[0], "value": est.split(" ")[0]
            } for est in COORDINATES.keys()],
        ), dbc.InputGroupText("Estab")], className="p-0")
    ], className="m-2"),
    dbc.Row(id="files-list", className="m-2 p-0")
], className="mb-20")


@callback(
    Output("files-list", "children"),
    Input("update-files-button", "n_clicks"),
)
def tt(_s):
    return update_reports_list()

@callback(
    Output({"type": "file-collapse", "index": ALL}, "is_open"),
    Input("filter-report-date", "value"),
    Input("filter-report-estab", "value"),
    State("filter-report-date", "value"),
    State("filter-report-estab", "value"),
)
def filter_files(_1, _2, date, estab):
    files = listdir(CFG.data)
    files = sorted(files, reverse=True)
    states = [False] * len(files)
    for i, file in enumerate(files):
        include = True
        if date != "Todos" and date not in file:
            include = False
        if estab != "Todos" and estab not in file:
            include = False
        states[i] = include
    return states


@callback(
    Output({'type': 'file-modal', 'index': MATCH}, 'is_open'),
    Output({'type': 'file-modal', 'index': MATCH}, 'children'),
    Input({'type': 'file-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'file-modal', 'index': MATCH}, 'is_open'),
    State('password-report', 'value'),
    prevent_initial_call=True
)
def toggle_modal(n_clicks, is_open, password):
    if is_open:
        return False, dash.no_update
    # Retrieve password
    ADM_PASSWORD = getenv("ADM_PASSWORD")
    if password != ADM_PASSWORD or ADM_PASSWORD is None:
        return dash.no_update, dash.no_update

    # Load the specific file corresponding to the triggered index
    files = listdir(CFG.data)
    files = sorted(files, reverse=True)

    triggered_id = ctx.triggered_id["index"]
    file = files[triggered_id]
    df = pd.read_csv(join(CFG.data, file))
    df_data = df.to_string(index=False)
    parts = file.split("|")
    modal_content = dbc.Col([
        dbc.ModalHeader(dbc.Stack([
            dbc.Label(f"{parts[0]}, {parts[2]}"), dbc.Label(parts[3])
        ]), style=BOLD, close_button=False),
        dbc.ModalBody(
            html.Pre(df_data, style={"font-size": "0.8em"}, className="m-2")),
        dbc.ModalFooter("Fechar", style=BOLD)
    ])
    return True, modal_content
