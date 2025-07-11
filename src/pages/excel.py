from datetime import datetime
import dash
from dash import html, callback, Input, Output, State, dcc
from CONFIG import BOLD, CFG
from dateutil.relativedelta import relativedelta
import dash_bootstrap_components as dbc
from os import getenv
from os.path import join, exists
from dotenv import load_dotenv
from components import info_nav
from tools import aggregate_reports


dash.register_page(__name__)
load_dotenv()


layout = html.Div([
    info_nav(__name__),
    dbc.Alert([
        html.H5([
            html.I(className="bi bi-info-circle-fill"),
            " Instruções e definições", html.Hr(className="m-1")
        ], className="alert-heading", style=BOLD),
        dcc.Markdown([
            "Só é possível atualizar quando a senha correta está no campo "
            "abaixo. Somente use quando necessário!\n"
            "Selecione o mês da planilha. "
            "Clique em 'Baixar' para gerar o arquivo Excel.",
        ], style={'whiteSpace': 'pre-line'}, className="mb-0")
    ], dismissable=False, color="warning"),
    dbc.Stack([
        html.H1("Excel"), html.Div(className="mx-auto"),
        dbc.Stack([
            dbc.Select(
                id="month-excel",
                persistence=True, persistence_type="local"
            ),
            dcc.Loading(
                dbc.Button("Baixar", id="refresh-excel"))
        ], direction="horizontal")
    ], direction="horizontal", className="m-2"),
    dbc.Row(dbc.InputGroup([
        dbc.Input(
            debounce=True, id="excel-password", type="text", persistence=True),
        dbc.InputGroupText("Senha"),
    ], class_name="p-0"), className="m-2"),
    dcc.Download(id="download-excel"),
    dbc.Row(html.H6(id="excel-info"), className="m-2")
], className="mb-20")


@callback(
    Output("month-excel", "options"),
    Input('refresh-excel', 'n_clicks'),
)
def unlock_content(_):
    now = datetime.now()
    current_date = datetime(now.year, now.month, 1)
    dts = [
        (current_date - relativedelta(months=i)).strftime("%Y-%m")
        for i in range(0, CFG.report_timeout_months + 1)]
    return dts


@callback(
    Output("download-excel", "data"),
    Output("excel-info", "children"),
    Input("refresh-excel", "n_clicks"),
    State("month-excel", "value"),
    State("excel-password", "value"),
    prevent_initial_call=True
)
def download_excel(_, month, password):
    if month is None:
        return dash.no_update, "Selecione um mês."
    ADM_PASSWORD = getenv("ADM_PASSWORD")
    if password != ADM_PASSWORD:
        return dash.no_update, "Senha incorreta"
    aggregate_reports(month.split("-"))
    path = join(CFG.data_agg, f"{month.replace('-', '_')}_Coleta.xlsx")
    if exists(path):
        return dcc.send_file(path), "Download iniciado."
    return dash.no_update, "Erro ao gerar o arquivo ou dados faltando."
