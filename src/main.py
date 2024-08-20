# flake8: noqa: E402
import hashlib
from dash import Dash, dcc, html, _dash_renderer, Output, Input, callback
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_auth
import sys
from os.path import join, dirname
from os import getenv, listdir
from dotenv import load_dotenv
from flask import Response, jsonify, request, send_from_directory

sys.path.append(join(dirname(__file__), "pages"))
sys.path.append(dirname(__file__))
_dash_renderer._set_react_version("18.2.0")

from CONFIG import CFG, COORDINATES
load_dotenv()

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

app.layout = dmc.MantineProvider(html.Div([
    dcc.Store(
        id="grid-data", storage_type="local",
        data=[[{}] * CFG.product_rows[prd] for prd in CFG.products]),
    dcc.Store(id="info-data", storage_type="local", data=[None]*3),
    dcc.Store(id="config", storage_type="local", data=vars(CFG)),
    dcc.Store(id="coordinates", storage_type="local", data=COORDINATES),
    dcc.Store(id="geo-history", storage_type="local", data=[]),
    dcc.Store(id="files-hash", storage_type="local", data=[0, 0]),
    dcc.Store(id="files-data", storage_type="local", data=[{}]),
    html.Canvas(id="confetti", className="foregroundAbsolute"),
    dash.page_container
]), id="mantine")


@callback(
    Output('config', 'data'),
    Output('grid-data', 'data'),
    Output('info-data', 'data'),
    Input('config', 'data'),
)
def check_version(config):
    if config is None or CFG.version != config.get('version'):
        out = [vars(CFG)]
        out.append([[{}] * CFG.product_rows[prd] for prd in CFG.products])
        out.append([None]*3)
        return out
    return dash.no_update


@callback(
    Output('coordinates', 'data'),
    Input('coordinates', 'data')
)
def check_version2(coords):
    if coords is None or COORDINATES["version"] != coords.get('version'):
        return COORDINATES
    return dash.no_update


@server.route('/data_agg_csv/<path:filename>')
def download_file(filename):
    return send_from_directory(CFG.data_agg_csv, f"{filename}_Coleta.csv")


@server.route('/get-file-names', methods=['POST'])
def get_file_names() -> Response:
    client_hash = request.json.get('hash', '')
    file_names = sorted(listdir(CFG.data))
    server_hash = hashlib.md5(''.join(file_names).encode()).hexdigest()

    if client_hash == server_hash:
        return jsonify({"updated": True})
    return jsonify({"updated": False, "file_names": file_names, "hash": server_hash})


if __name__ == "__main__":
    match getenv("TEST"):
        case "reloader":
            app.run_server(
                port="8060", dev_tools_hot_reload=True, use_reloader=True)
        case "debug":
            app.run_server(
                port="8060", debug=True,
                dev_tools_hot_reload=True, use_reloader=True)
        case _:
            app.run_server(host="0.0.0.0", port="8060")
