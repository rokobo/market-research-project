from datetime import datetime
from os import getenv
from dateutil.relativedelta import relativedelta
import dash
import dash_ag_grid as dag
from dash import html, Input, Output, dcc, clientside_callback, \
    ClientsideFunction, callback, State
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
from CONFIG import CFG, BOLD
from tools import aggregate_reports

dash.register_page(__name__)
load_dotenv()

now = datetime.now()
current_date = datetime(now.year, now.month, 1)

layout = html.Div([
    dbc.Alert([
        html.H5([
            html.I(className="bi bi-info-circle-fill"),
            " Instruções e definições", html.Hr(className="m-1")
        ], className="alert-heading", style=BOLD),
        dcc.Markdown(
            '''
            Selecione o mês e os produtos que deseja visualizar. Clique em "Atualizar" para gerar o relatório.

            Somente atualize a tabela quando necessário!''',
            style={'whiteSpace': 'pre-line'}, className="mb-0")
    ], dismissable=False, color="warning"),
    dbc.Stack([
        html.H1("Resultados"),
        html.H6(className="mx-auto"),
        dbc.Stack([
            dbc.Select(
                id="month-result",
                options=[
                    (current_date - relativedelta(months=i)).strftime("%Y-%m")
                    for i in range(0, CFG.report_timeout_months + 1)],
                persistence=True, persistence_type="local"
            ),
            dbc.Button("Atualizar", id="refresh-result", disabled=True)
        ], direction="horizontal")
    ], direction="horizontal", className="m-2"),
    dbc.Row(
        dbc.Input(
            id="password-result", type="text", debounce=True,
            placeholder="Senha de administrador", persistence=True,
            persistence_type="local"),
        className="m-2"),
    dbc.Row(
        dbc.Checklist(
            options=CFG.excel_products, id="products-result", inline=True,
            persistence=True, persistence_type="local"),
        className="m-2"),
    dbc.Row(
        dag.AgGrid(
            id="ag-grid-result",
            rowData=[{}],
            columnDefs=[
                {'field': 'Produto'},
                {'field': 'Preço'},
                {'field': 'Quantidade'},
            ],
            columnSize="responsiveSizeToFit",
            defaultColDef={
                "editable": False,
                "sortable": True,
                "resizable": True,
                "wrapText": True,
                "cellStyle": {
                    "padding": 0,
                    "wordBreak": "normal",
                    "lineHeight": "unset"
                },
            },
            dashGridOptions={
                "animateRows": True,
                "domLayout": "autoHeight",
                'headerHeight': 30,
            },
            style={"height": None},
            className="p-0 ag-theme-material"
        ), className="m-2"
    )

])


@callback(
    Output('refresh-result', 'disabled'),
    Input('password-result', 'value'),
)
def unlock_content(password):
    ADM_PASSWORD = getenv("ADM_PASSWORD")
    return not ((password == ADM_PASSWORD) and (ADM_PASSWORD is not None))


@callback(
    Output("ag-grid-result", "rowData"),
    Input("refresh-result", "n_clicks"),
    State("month-result", "value"),
    State("products-result", "value"),
    prevent_initial_call=True
)
def update_result(_, month, products):
    if (month is None) or (products in [None, []]):
        return dash.no_update
    df = aggregate_reports(month.split("-"), True)
    df = df[['Produto', 'Preço', 'Quantidade']]
    df = df.groupby('Produto').agg(
        {'Preço': 'mean', 'Quantidade': 'mean'}).reset_index()
    df['Preço'] = df['Preço'].round(3)
    return df[df['Produto'].isin(products)].to_dict(orient='records')
