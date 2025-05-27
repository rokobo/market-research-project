from os import getenv
import dash
from os.path import join
import dash_bootstrap_components as dbc
from dash import html, Input, Output, callback, State, ctx
import pandas as pd
import sqlite3 as sql
from CONFIG import CFG, BOLD
from components import adm_nav

dash.register_page(__name__)

layout = html.Div([
    adm_nav(__name__),
    dbc.Alert([
        html.H4([
            html.I(className="bi bi-info-circle-fill"),
            " Instruções de uso", html.Hr(className="m-1")
        ], className="alert-heading", style=BOLD),
        html.P([
            "Clique em atualizar para baixar as tabelas de marcas. "
            "O nome das marcas será automaticamente capitalizado"
            "(todas as palavras). A prioridade"
            " indica a ordem de exibição das marcas na tabela de produtos. "
            "Quanto maior o número, mais baixa a prioridade. "
        ], className="mb-0", style={'whiteSpace': 'pre-line'}),
    ], dismissable=False, color="warning"),
    dbc.Stack([
        html.H1("Marcas"),
        html.Div(className="mx-auto"),
        dbc.Button("Atualizar", id="update-db-brands")
    ], direction="horizontal", className="m-2"),
    dbc.Row([
        dbc.InputGroup([
            dbc.Input(id="brands-password", type="text", persistence=True),
            dbc.InputGroupText("Senha"),
        ], class_name="p-0"),
        dbc.InputGroup([
            dbc.Select(
                id="select-brand-table", options=[], value="",
                placeholder="Selecione uma tabela"),
            dbc.InputGroupText("Tabela"),
        ], className="p-0")
    ], className="m-2"),
    dbc.Row(id="brands-alert", className="m-2"),
    dbc.Row(dash.dash_table.DataTable(
        id="brands-edit-table",
        editable=True,
        row_deletable=True,
        sort_action="native",
        sort_by=[{"column_id": "priority", "direction": "asc"}],
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "right"},
    ), className="m-2"),
    html.Br(),
    dbc.Stack([
        dbc.Button("Adicionar Marca", id="add-brand", color="primary"),
        html.Div(className="mx-auto"),
        dbc.Button("Salvar Alterações", id="save-brands", color="success"),
    ], className="m-2", direction="horizontal"),
])

with sql.connect(join(CFG.config_folder, "marcas.db")) as db:
    for product in CFG.products:
        if CFG.product_fields[product][0] == 1:
            db.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {product} (
                    brand TEXT NOT NULL UNIQUE,
                    priority INTEGER NOT NULL
                )
                """
            )
        else:
            db.execute(f"DROP TABLE IF EXISTS {product}")
    db.commit()


@callback(
    Output("select-brand-table", "options"),
    Output("select-brand-table", "value"),
    Output('brands-edit-table', 'columns'),
    Output('brands-edit-table', 'data'),
    Output("brands-alert", "children"),
    Input("update-db-brands", "n_clicks"),
    Input("select-brand-table", "value"),
    Input("add-brand", "n_clicks"),
    Input("save-brands", "n_clicks"),
    State('brands-edit-table', 'data'),
    State('brands-edit-table', 'columns'),
    State("brands-password", "value"),
    prevent_initial_call=True
)
def handle_brands(_clicks, table, add_clk, save_clk, rows, columns, password):
    # Check password
    ADM_PASSWORD = getenv("ADM_PASSWORD")
    if password != ADM_PASSWORD:
        return dash.no_update

    context = ctx.triggered_id
    alert = ""
    with sql.connect(join(CFG.config_folder, "marcas.db")) as db:
        tables = pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table';", db).values

    if not table:
        table = tables[0][0]

    options = [  # Dont show split products
        {"label": t[0], "value": t[0]}
        for t in tables
        if t[0] not in CFG.product_splits]

    # Save brands
    if context == "save-brands":
        col_names = [col["id"] for col in columns]
        try:
            with sql.connect(join(CFG.config_folder, "marcas.db")) as db:
                # Get NOT NULL columns from table schema
                schema = pd.read_sql(f"PRAGMA table_info({table})", db)
                not_null_cols = schema[schema["notnull"] == 1]["name"].tolist()

                # Normalize "brand" column: capitalize each word
                for idx, row in enumerate(rows):
                    brand_val = row.get("brand", None)
                    if brand_val not in (None, '', []):
                        # Capitalize each word, strip whitespace
                        normalized = " ".join(
                            word.capitalize()
                            for word in str(brand_val).strip().split())
                        rows[idx]["brand"] = normalized

                # Always validate NOT NULL columns before saving
                for idx, row in enumerate(rows):
                    for col in not_null_cols:
                        if row.get(col, None) in (None, '', []):
                            alert_msg = f"Erro: O campo obrigatório '{col}'"
                            alert_msg += f" está vazio na linha {idx+1}."
                            alert = dbc.Alert(
                                alert_msg, color="danger", dismissable=True)
                            # Return without reloading from DB
                            return options, table, columns, rows, alert

                # Check that "priority" column has only INTEGER values
                for idx, row in enumerate(rows):
                    value = row.get("priority", None)
                    if value not in (None, '', []):
                        try:
                            int_value = int(value)
                            if str(int_value) != str(value).strip():
                                raise ValueError
                        except Exception:
                            alert_msg = "Erro: O campo 'priority' deve conter"
                            alert_msg += " apenas valores numéricos"
                            alert_msg += f" (linha {idx+1})."
                            alert = dbc.Alert(
                                alert_msg, color="danger", dismissable=True)
                            return options, table, columns, rows, alert

                # Check for UNIQUE constraint violations
                values = [row.get("brand", None) for row in rows]
                for idx, val in enumerate(values):
                    if val not in (None, '', []) and values.count(val) > 1:
                        alert_msg = "Erro: O campo único 'brand' está "
                        alert_msg += f"duplicado na linha {idx+1}."
                        alert = dbc.Alert(
                            alert_msg, color="danger", dismissable=True)
                        return options, table, columns, rows, alert

                db.execute(f"DELETE FROM {table}")
                placeholders = ", ".join(["?"] * len(col_names))
                insert_sql = f"INSERT INTO {table} ({', '.join(col_names)}) "
                insert_sql += f"VALUES ({placeholders})"
                for row in rows:
                    values = [row.get(col, None) for col in col_names]
                    db.execute(insert_sql, values)
                db.commit()
            alert = dbc.Alert(
                "Alterações salvas com sucesso!",
                color="success", dismissable=True)
        except Exception as e:
            alert = dbc.Alert(
                f"Erro ao salvar: {str(e)}", color="danger", dismissable=True)

    # Add brand
    if context == "add-brand":
        if columns:
            rows = rows or []
            rows.append({c['id']: '' for c in columns})

    # Always reload data from DB except when adding a row
    if context != "add-brand":
        with sql.connect(join(CFG.config_folder, "marcas.db")) as db:
            data = pd.read_sql(f"SELECT * FROM {table}", db)
        columns = [
            {"name": i, "id": i, "editable": True} for i in data.columns]
        rows = data.to_dict("records")

    return options, table, columns, rows, alert
