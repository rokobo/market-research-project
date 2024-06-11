from dash import Dash, html, dcc
import dash
import dash_bootstrap_components as dbc
import sys
from os.path import join, dirname


sys.path.append(join(dirname(__file__), "pages"))
sys.path.append(dirname(__file__))

app = Dash(
    title="test title", update_title=None,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    assets_folder='../assets'
)

app.layout = [
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
]

if __name__ == "__main__":
    app.run(
        debug=True,
        port="8050",
        dev_tools_hot_reload=True,
        use_reloader=True
    )
