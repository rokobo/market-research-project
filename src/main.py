# flake8: noqa: E402
import hashlib
from dash import Dash, dcc, html, _dash_renderer, Output, Input, callback, \
    clientside_callback, ClientsideFunction, State
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_auth
import sys
from os.path import join, dirname, exists
from os import getenv, listdir, remove
from dotenv import load_dotenv
from flask import Response, jsonify, request, send_from_directory
import pandas as pd
from time import localtime, strftime
import json

sys.path.append(join(dirname(__file__), "pages"))
sys.path.append(dirname(__file__))
_dash_renderer._set_react_version("18.2.0")

from CONFIG import CFG, COORDINATES
from tools import create_group_pages, load_brands
load_dotenv()
create_group_pages(CFG.unique_groups)


THEMES = {
    "🌞 Light": dbc.themes.BOOTSTRAP,
    "🌞 Flatly": dbc.themes.FLATLY,
    "🌞 Litera": dbc.themes.LITERA,
    "🌞 Zephyr": dbc.themes.ZEPHYR,
    "🌙 Superhero": dbc.themes.SUPERHERO,
    "🌙 Dark": dbc.themes.DARKLY,
    "🌙 Solar": dbc.themes.SOLAR,
    "🌙 Vapor": dbc.themes.VAPOR,
}

app = Dash(
    title="ICB", update_title="ICB...",
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    use_pages=True, assets_folder='../assets',
    compress=True
)

server = app.server
assert server is not None
server.secret_key = getenv('SECRET_KEY')

auth = dash_auth.BasicAuth(
    app,
    {getenv("APP_USERNAME"): getenv("APP_PASSWORD")}
)

app.layout = html.Div([
    dcc.Store(id="geo-history", storage_type="local", data=[]),
    dcc.Store(id="CFG-data", storage_type="local", data=vars(CFG)),
    dcc.Store(id="brands", storage_type="local"),
    html.Canvas(id="confetti", className="foregroundAbsolute"),
    dcc.Geolocation(id="geolocation", high_accuracy=True, update_now=True),
    html.Div(
        dbc.Stack([
            dbc.Button("Status", color="info", size="sm", id="status-button"),
            dbc.Select(
                options=[{"label": k, "value": v} for k, v in THEMES.items()],
                persistence=True, persistence_type="local",
                persisted_props=["value"], placeholder="Tema",
                id="theme-select", size="sm",
            ),
        ], direction="horizontal"),
        style={"position": "fixed", "bottom": 0, "left": 0, "zIndex": 5}),
    dbc.Modal([
        dbc.ModalHeader(id="server-status-header"),
        dbc.ModalBody(id="server-status-body"),
    ], id="server-status-modal", size="lg", is_open=False, scrollable=True),
    html.Div(
        dbc.Stack([
            dbc.Badge("Calc...", color="danger", id="geolocation-badge"),
        ], direction="horizontal"),
        style={"position": "fixed", "bottom": 0, "right": 0, "zIndex": 5}),
    html.Link(id="theme-link", rel="stylesheet"),
    dash.page_container,
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
])


clientside_callback(
    ClientsideFunction(
        namespace='functions',
        function_name='theme_select'
    ),
    Output("theme-link", "href"),
    Input("theme-select", "value")
)


@server.route("/get-cfg")
def get_cfg():
    return jsonify(vars(CFG))


@server.route("/get-brands/<product>")
def get_brands(product):
    brands = load_brands(product)
    return jsonify(brands)


@callback(
    Output("server-status-header", "children"),
    Output("server-status-body", "children"),
    Output("server-status-modal", "is_open"),
    Input("status-button", "n_clicks"),
    State("server-status-modal", "is_open")
)
def server_status(n_clicks, is_open):
    if n_clicks is None:
        return dash.no_update, dash.no_update, dash.no_update
    body = []
    header = f"Status atualizado: {strftime("%H:%M:%S", localtime())}"
    files = listdir(CFG.data)
    files.sort(reverse=True)
    files = files[:3]

    body.append(html.P(
        f"Últimos relatórios:", style={"font-weight": "bold"}))
    tabs = []
    for file in files:
        parts = file.split('|')
        df = pd.read_csv(join(CFG.data, file))
        df_data = df.to_string(index=False)
        tabs.append(dbc.Tab(
            html.Pre(df_data, style={"font-size": "0.8em"}),
            label=f"{parts[0]}, {parts[2]}, {parts[3]}"))
    body.append(dbc.Tabs(tabs))
    return header, body, True


@server.route('/data_agg_csv/<path:filename>')
def download_file(filename):
    return send_from_directory(CFG.data_agg_csv, f"{filename}_Coleta.csv")


@server.route('/get-file-info', methods=['POST'])
def get_file_names() -> Response:
    file_names = sorted([i for i in listdir(CFG.data) if i.endswith('.csv')])
    info = {}
    for name in file_names:
        df = pd.read_csv(join(CFG.data, name))
        obs_name = name.replace('.csv', '.txt')
        obs_name = join(CFG.data_obs, obs_name)
        if exists(obs_name):
            with open(obs_name, 'r') as obs_file:
                obs = obs_file.read().strip()
        else:
            obs = "Sem observações"
        obs = obs.split('Histórico de geolocalização')[0]
        df.Marca = df.Marca.fillna("SEM MARCA")
        info[name] = df.groupby('Produto').apply(lambda x: {
            'Quant': len(x['Marca']),
            'Marca': x['Marca'].value_counts().to_dict()
        }, include_groups=False).to_dict()
        info[name]['obs'] = obs.strip()
    return jsonify({"info": info})


if __name__ == "__main__":
    match getenv("TEST"):
        case "reloader":
            app.run(
                port="8060", dev_tools_hot_reload=True, use_reloader=True)
        case "debug":
            app.run(
                port="8060", debug=True, host="0.0.0.0",
                dev_tools_hot_reload=True, use_reloader=True,
                ssl_context=("cert.pem", "key.pem"))
        case _:
            app.run(host="0.0.0.0", port="8060")
