# flake8: noqa: E501
from os import getenv
import dash
from dateutil.relativedelta import relativedelta
from datetime import datetime
import dash_ag_grid as dag
from dash import html, Input, Output, dcc, callback, State
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import pandas as pd
from CONFIG import CFG, BOLD
from tools import aggregate_reports
from components import adm_nav

dash.register_page(__name__)
load_dotenv()


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

            Selecione o mês e os produtos que deseja visualizar. Clique em "Atualizar" para gerar o relatório.''',
            style={'whiteSpace': 'pre-line'}, className="mb-0")
    ], dismissable=False, color="warning"),
    dbc.Stack([
        html.H1("Resultados"),
        html.H6(className="mx-auto"),
        dbc.Stack([
            dbc.Select(
                id="month-result",
                persistence=True, persistence_type="local"
            ),
            dbc.Button("Atualizar", id="refresh-result")
        ], direction="horizontal")
    ], direction="horizontal", className="m-2"),
    dbc.Row(
        dbc.Checklist(
            options=CFG.excel_products, id="products-result", inline=True,
            persistence=True, persistence_type="local"),
        className="m-2"),
    html.Br(className="m-2"),
    dbc.Row(html.Pre(
        id="result-table", style={"font-size": "1.2em", "text-align": "center"}
    ), className="m-2")

])


@callback(
    Output("month-result", "options"),
    Input("refresh-result", "n_clicks"),
)
def unlock_content(password):
    now = datetime.now()
    current_date = datetime(now.year, now.month, 1)
    dts = [
        (current_date - relativedelta(months=i)).strftime("%Y-%m")
        for i in range(0, CFG.report_timeout_months + 1)]
    return dts


@callback(
    Output("result-table", "children"),
    Input("refresh-result", "n_clicks"),
    State("month-result", "value"),
    State("products-result", "value"),
    prevent_initial_call=True
)
def update_result(_, month, products):
    if (month is None) or (products in [None, []]):
        return dash.no_update
    df = aggregate_reports(month.split("-"), True)
    if df is None:
        return "Sem dados"
    df = df[['Produto', 'Preço', 'Quantidade']]
    df = df.groupby('Produto').agg(
        {'Preço': 'mean', 'Quantidade': 'mean'}).reset_index()
    df['Preço'] = df['Preço'].round(3)
    df['Quantidade'] = df['Quantidade'].round(3)
    return df[df['Produto'].isin(products)].to_string(index=False)
