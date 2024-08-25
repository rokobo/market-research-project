# flake8: noqa: E501
from datetime import datetime
import dash
from dash import html, callback, Input, Output, State, dcc, \
    clientside_callback, ClientsideFunction
from CONFIG import BOLD, CFG
from dateutil.relativedelta import relativedelta
import dash_bootstrap_components as dbc
from os import getenv
from os.path import join, exists
import dash_ag_grid as dag
from dotenv import load_dotenv
from components import adm_nav
from tools import aggregate_reports


dash.register_page(__name__)
load_dotenv()
now = datetime.now()
current_date = datetime(now.year, now.month, 1)


layout = html.Div([
    adm_nav(__name__),
    dbc.Alert([
        html.H5([
            html.I(className="bi bi-info-circle-fill"),
            " Instruções e definições", html.Hr(className="m-1")
        ], className="alert-heading", style=BOLD),
        dcc.Markdown(
            '''
            Só é possível atualizar quando a senha correta está no campo abaixo. Somente use quando necessário!

            Selecione o mês da planilha. Clique em "Baixar" para gerar o arquivo Excel.''',
        style={'whiteSpace': 'pre-line'}, className="mb-0")
    ], dismissable=False, color="warning"),
    dbc.Stack([
        html.H1("Excel"), html.Div(className="mx-auto"),
        dbc.Stack([
            dbc.Select(
                id="month-excel",
                options=[
                    (current_date - relativedelta(months=i)).strftime("%Y-%m")
                    for i in range(0, CFG.report_timeout_months + 1)],
                persistence=True, persistence_type="local"
            ),
            dcc.Loading(
                dbc.Button("Baixar", id="refresh-excel", disabled=True))
        ], direction="horizontal")
    ], direction="horizontal", className="m-2"),
    dcc.Download(id="download-excel"),
    dbc.Row(
        dbc.Input(
            id="password-excel", type="text", debounce=True,
            placeholder="Senha de administrador", persistence=True,
            persistence_type="local"
    ), className="m-2"),
    dbc.Row(html.H6(id="excel-info"), className="m-2")
], className="mb-20")


@callback(
    Output('refresh-excel', 'disabled'),
    Input('password-excel', 'value'),
)
def unlock_content(password):
    ADM_PASSWORD = getenv("ADM_PASSWORD")
    return not ((password == ADM_PASSWORD) and (ADM_PASSWORD is not None))


@callback(
    Output("download-excel", "data"),
    Output("excel-info", "children"),
    Input("refresh-excel", "n_clicks"),
    State("month-excel", "value"),
    prevent_initial_call=True
)
def download_excel(_, month):
    if month is None:
        return dash.no_update, "Selecione um mês."
    aggregate_reports(month.split("-"))
    path = join(CFG.data_agg, f"{month.replace('-', '_')}_Coleta.xlsx")
    if exists(path):
        return dcc.send_file(path), "Download iniciado."
    return dash.no_update, "Erro ao gerar o arquivo ou dados faltando."
