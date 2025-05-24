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

sys.path.append(join(dirname(__file__), "pages"))
sys.path.append(dirname(__file__))
_dash_renderer._set_react_version("18.2.0")

from CONFIG import CFG, COORDINATES
from tools import create_group_pages
load_dotenv()
create_group_pages()


app = Dash(
    title="ICB", update_title="ICB...",
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    use_pages=True, assets_folder='../assets',
    compress=False
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
    html.Canvas(id="confetti", className="foregroundAbsolute"),
    dbc.Alert(
        id="geo-loading-modal", className="m-2",
        dismissable=False, color="danger",
        style={
            "position": "fixed", "bottom": 25, "left": 0, "zIndex": 5,
            "width": "100%"
        },
    ),
    dcc.Geolocation(id="geolocation", high_accuracy=True, update_now=True),
    dcc.Interval(id="10-seconds", interval=5*1000),
    dbc.Button(
        "Status", color="info", size="sm", id="status-button",
        style={"position": "fixed", "bottom": 0, "left": 0, "zIndex": 5}),
    dbc.Modal([
        dbc.ModalHeader(id="server-status-header"),
        dbc.ModalBody(id="server-status-body"),
    ], id="server-status-modal", size="lg", is_open=False, scrollable=True),
    html.Div(
        dbc.Stack([
            dbc.Badge("", color="primary", id="size-badge"),
            dbc.Badge("", color="secondary", id="geolocation-badge"),
            dbc.Badge("", color="success", id="online-badge"),
        ], direction="horizontal"),
        style={"position": "fixed", "bottom": 0, "right": 0, "zIndex": 5}),
    dash.page_container,
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
])


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
    State('geo-history', 'data'),
)

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
            app.run_server(
                port="8060", dev_tools_hot_reload=True, use_reloader=True)
        case "debug":
            app.run_server(
                port="8060", debug=True, host="0.0.0.0",
                dev_tools_hot_reload=True, use_reloader=True)
        case _:
            app.run_server(host="0.0.0.0", port="8060")
