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
from components import adm_nav, create_database_mod

dash.register_page(__name__)
load_dotenv()

with sql.connect(join(CFG.config_folder, "products.db")) as db:
    config = pd.read_sql("SELECT * FROM products", db)
config.drop(columns=["product"], inplace=True)
layout = html.Div([
    adm_nav(__name__),
    dbc.Stack([
        html.H1("Produtos"), html.Div(className="mx-auto"),
        dbc.Button("Atualizar", id="update-db-products")
    ], direction="horizontal", className="m-2"),
    dbc.Row([dbc.InputGroup([
        dbc.Select(options=config.columns, id="select-attribute-products", value="group"),
        dbc.InputGroupText("Atributo"),
    ], className="p-0")], className="m-2"),
    # create_database_mod("products"),
    html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),
])
