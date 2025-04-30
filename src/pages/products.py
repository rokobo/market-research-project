# flake8: noqa: E501
from os import getenv
import dash
from os.path import join
from dateutil.relativedelta import relativedelta
from datetime import datetime
import dash_ag_grid as dag
from dash import html, Input, Output, dcc, callback, State, dash_table
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import pandas as pd
from CONFIG import CFG, BOLD
import sqlite3 as sql
from tools import aggregate_reports
from components import info_nav, create_database_mod

dash.register_page(__name__)
load_dotenv()

with sql.connect(join(CFG.config_folder, "products.db")) as db:
    config = pd.read_sql("SELECT * FROM products", db)
layout = html.Div([
    info_nav(__name__),
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
        html.H1("Produtos"), html.Div(className="mx-auto"),
        dbc.Button("Atualizar", id="update-db-products")
    ], direction="horizontal", className="m-2"),
    create_database_mod("products"),
    html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),
])
