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
load_dotenv()


app = Dash(
    title="test title", update_title=None,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    assets_folder='../assets'
)

app.server.secret_key = getenv('SECRET_KEY')

auth = dash_auth.BasicAuth(
    app,
    {getenv("APP_USERNAME"): getenv("APP_PASSWORD")}
)

app.layout = [
    dcc.Store(id="store", storage_type="local"),
    dcc.Store(id="load-flag", storage_type="local", data=False),
    html.Canvas(id="confetti"),
    dash.page_container,
]

if __name__ == "__main__":
    app.run(
        debug=True,
        port="8060",
        dev_tools_hot_reload=True,
        use_reloader=True
    )
