from dash import Dash, dcc, html, _dash_renderer
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_auth
import sys
from os.path import join, dirname
from os import getenv
from dotenv import load_dotenv
from flask import send_from_directory

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
    dcc.Store(id="store", storage_type="local", data=[]),
    dcc.Store(id="load-flag", storage_type="local", data=False),
    dcc.Store(id="config", storage_type="local", data=vars(CFG)),
    dcc.Store(id="coordinates", storage_type="local", data=COORDINATES),
    dcc.Store(id="geo-history", storage_type="local", data=[]),
    html.Canvas(id="confetti", className="foregroundAbsolute"),
    dash.page_container
]), id="mantine")


@server.route('/data_agg_csv/<path:filename>')
def download_file(filename):
    return send_from_directory(CFG.data_agg_csv, f"{filename}_Coleta.csv")


if __name__ == "__main__":
    match getenv("TEST"):
        case None:
            app.run_server(host="0.0.0.0", port="8060")
        case "reloader":
            app.run_server(
                port="8060", dev_tools_hot_reload=True, use_reloader=True)
        case "debug":
            app.run_server(
                port="8060", debug=True,
                dev_tools_hot_reload=True, use_reloader=True)
