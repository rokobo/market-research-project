from dash import Dash, dcc, html
import dash
import dash_bootstrap_components as dbc
import dash_auth
import sys
from os.path import join, dirname
from os import getenv
from dotenv import load_dotenv

sys.path.append(join(dirname(__file__), "pages"))
sys.path.append(dirname(__file__))
from CONFIG import CFG
load_dotenv()


app = Dash(
    title="ICB", update_title="ICB...",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True, assets_folder='../assets',
    compress=False
)

app.server.secret_key = getenv('SECRET_KEY')

server = app.server

auth = dash_auth.BasicAuth(
    app,
    {getenv("APP_USERNAME"): getenv("APP_PASSWORD")}
)

app.layout = html.Div([
    dcc.Store(id="store", storage_type="local", data=[]),
    dcc.Store(id="load-flag", storage_type="local", data=False),
    dcc.Store(id="config", storage_type="local", data=vars(CFG)),
    html.Canvas(id="confetti", className="foregroundAbsolute"),
    dash.page_container
])

if __name__ == "__main__":
    app.run_server(
        host="0.0.0.0",
        port="8060",
        # debug=True,
        # dev_tools_hot_reload=True,
        # use_reloader=True
    )
