"""Tools for the pages."""

from functools import cache
import math
from os.path import join, exists
from os import makedirs, listdir
from send2trash import send2trash
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Any, Optional
from CONFIG import CFG


def load_establishments() -> list[dict[str, str]]:
    establishments = []
    with open(join(CFG.home, "config/estabelecimentos.txt"), 'r') as file:
        for line in file:
            est = line.strip()
            establishments.append({
                "label": est, "value": est
            })
    return establishments


def load_brands(product: str) -> list[dict[str, str]]:
    brands = []
    with open(join(CFG.home, f"config/marcas-{product}.txt"), 'r') as file:
        for line in file:
            brand = line.strip()
            if brand == "-p":
                brands.append({
                    "label": "Preferenciais",
                    "value": brand, "disabled": True
                })
            elif brand == "-np":
                brands.append({
                    "label": "Não Preferenciais",
                    "value": brand, "disabled": True
                })
            else:
                brands.append({
                    "label": brand, "value": brand
                })
    return brands


@cache
def load_raw_brands(product: str) -> Optional[list[dict[str, str]]]:
    brands = []
    path = join(CFG.home, f"config/marcas-{product}.txt")
    if not exists(path):
        return None
    with open(path, 'r') as file:
        for line in file:
            brand = line.strip()
            if brand == "-p":
                continue
            elif brand == "-np":
                continue
            else:
                brands.append(brand)
    return brands


def check_folder(path):
    if not exists(path):
        makedirs(path, exist_ok=True)


def save_products(
    data, info, obs: Optional[str],
    position: Optional[dict[str, Any]], geo_hist: Optional[list], test=False
):
    check_folder(CFG.data)
    check_folder(CFG.data_obs)

    df = pd.DataFrame([
        row | {"Produto": prd}
        for rows, prd in zip(data, CFG.products)
        for row in rows
    ], columns=["Produto", "Marca", "Preço", "Quantidade"])
    df = df.dropna(subset=["Preço"]).reset_index(drop=True)

    df["Nome"] = info[0]
    df["Data"] = info[1]
    df["Estabelecimento"] = info[2].split(" ")[0]
    df = df[[
        "Nome", "Data", "Estabelecimento", "Produto",
        "Marca", "Preço", "Quantidade"]]
    if test:
        return df
    file_name = f"{info[1]}|{int(time.time())}|{info[0]}|{info[2]}"

    if isinstance(position, list) and len(position) == 3:
        file_name += f"|{position[0]}|{position[1]}"
    df.to_csv(
        f"data/{file_name}.csv",
        index=False)

    obs_data = []
    if (obs is not None) and (obs != ""):
        obs_data.append(f"{obs}\n")
    else:
        obs_data.append("Sem observações\n")
    if geo_hist is not None:
        obs_data.append("\nHistórico de geolocalização\n")
        for geo_data in geo_hist:
            obs_data.append(f"{geo_data[2]}: {geo_data[0]}, {geo_data[1]}\n")
    if obs_data != []:
        with open(f"data_obs/{file_name}.txt", "w") as f:
            f.writelines(obs_data)
    return


def delete_old_reports():
    now = datetime.now()
    current_date = datetime(now.year, now.month, 1)
    months_ago = current_date - relativedelta(months=CFG.report_timeout_months)
    scheduled_delete = []
    for file in listdir(CFG.data):
        if not file.endswith(".csv"):
            continue
        year, month, day = file.split("|")[0].split("-")
        file_datetime = datetime(int(year), int(month), int(day))
        if file_datetime < months_ago:
            scheduled_delete.append(file)

    if scheduled_delete == []:
        print("No old files to delete")
        return

    print("Old files to delete:\n", "\n".join(scheduled_delete))

    for file in scheduled_delete:
        send2trash(join(CFG.home, f"data/{file}"))
    print("Old files deleted")


def aggregate_reports(date, test=False):
    # Collect all reports into a single dataframe
    reports = []
    check_folder(CFG.data_agg)
    check_folder(CFG.data_agg_csv)
    assert len(date[0]) == 4, date
    assert len(date[1]) == 2, date

    # Load all reports for the given month
    for file in listdir(CFG.data):
        if not file.endswith(".csv"):
            continue
        file_date = file.split("|")[0].split("-")
        if file_date[0] != date[0]:
            continue
        if file_date[1] != date[1]:
            continue

        df = pd.read_csv(join(CFG.home, f"data/{file}"))
        if df.empty:
            continue
        # Skip test reports
        if "TESTE" in df.loc[0, "Estabelecimento"]:
            continue
        reports.append(df)

    if reports == []:
        print("No valid reports found")
        return
    print("Number of reports: ", len(reports))

    # Concatenate all reports
    coleta_mes = pd.concat(reports)
    coleta_mes.Marca = coleta_mes.Marca.fillna("")
    # Fill Quantidade if empty
    coleta_mes["Quantidade"] = coleta_mes["Quantidade"].fillna(
        coleta_mes["Produto"].map(lambda x: CFG.quantities.get(x, [np.nan])[0])
    )

    # Split banana into two products (Nanica and Prata)
    mask = coleta_mes['Produto'] == 'banana'
    coleta_mes.loc[
        mask, 'Produto'] += ' ' + coleta_mes.loc[mask, 'Marca']
    coleta_mes.loc[mask, "Marca"] = ""

    # Replace by the correct product names (e.g. "acucar" -> "Açúcar")
    coleta_mes["Produto"] = coleta_mes["Produto"].map(
        lambda x: x.replace(
            x.split()[0], CFG.product_titles[x.split()[0]].split(" - ")[0]
        ))

    coleta_mes.to_csv(join(
        CFG.home, f"data_agg_csv/{date[0]}_{date[1]}_Coleta.csv"), index=False)
    coleta_mes["PPK"] = [
        f"=F{idx}/G{idx}" for idx in range(2, 2 + coleta_mes.shape[0])]

    if test:
        return coleta_mes

    prd_count = coleta_mes["Produto"].nunique()
    est_count = coleta_mes["Estabelecimento"].nunique()

    # Create basic statistics for the reports
    ppk = "coleta_mes[PPK]"
    prd = "coleta_mes[Produto]"
    prc = "coleta_mes[Preço]"
    est = "coleta_mes[Estabelecimento]"
    date_col = f"{date[0]}/{date[1]}"
    balanco = pd.DataFrame([{
        "Data": date_col,
        "Produto": CFG.excel_products[i-2],
        "Média Preço": f"=ROUND(AVERAGEIFS({prc}, {prd}, B{i}), 3)",
        "Média Estab PPK": (
            f"=ROUND(AVERAGE(AVERAGEIFS({ppk}, {est},"
            f"UNIQUE(FILTER({est}, ({prd}=B{i}))), {prd}, B{i})), 3)"),
        "Média PPK": f"=ROUND(AVERAGEIFS({ppk}, {prd}, B{i}), 3)",
        "Registros": f"=COUNTIF({prd}, B{i})",
        "Min PPK": f'=ROUND(MINIFS({ppk}, {prd}, B{i}), 3)',
        "Max PPK": f"=ROUND(MAXIFS({ppk}, {prd}, B{i}), 3)",
        "σ PPK": f"=SINGLE(ROUND(STDEV.P(IF({prd}=B{i}, {ppk})) , 3))",
        "Outliers por PPK": (
            f'=TEXTJOIN(" | ", TRUE, FILTER(ROUND({ppk}, 2), ({prd}=B{i})'
            f' * (({ppk} < (D{i} - (I{i} * 4))) + '
            f'({ppk} > (D{i} + (I{i} * 4)))), "-"))'),
    } for i in range(2, prd_count + 2)])

    # Save
    with pd.ExcelWriter(
        join(CFG.home, f"data_agg/{date[0]}_{date[1]}_Coleta.xlsx"),
        engine="xlsxwriter", engine_kwargs={'options': {
            'use_future_functions': True, 'strings_to_numbers': True}}
    ) as writer:
        # Coleta_Mes
        coleta_mes.to_excel(
            writer, sheet_name="Coleta_Mes",
            index=False, header=False, startrow=1)
        workbook = writer.book
        worksheet = writer.sheets["Coleta_Mes"]
        worksheet.set_column("B:B", 10)
        worksheet.set_column("C:C", 18)
        worksheet.set_column("D:D", 18)
        worksheet.set_column("E:E", 18)
        worksheet.set_column("G:G", 13)
        rows, columns = coleta_mes.shape
        worksheet.add_table(0, 0, rows, columns - 1, {
            'columns': [{'header': column} for column in coleta_mes.columns],
            'name': 'coleta_mes'
        })
        worksheet.conditional_format(f'F2:F{coleta_mes.shape[0] + 1}', {
            'type': 'formula',
            'criteria': (
                '=ABS(H2 - VLOOKUP(D2, Balanço!B:I, 3, FALSE)) '
                '> VLOOKUP(D2, Balanço!B:I, 8, FALSE)*4'),
            'format': workbook.add_format({
                'bg_color':   '#FFC7CE', 'font_color': '#9C0006'})
        })

        # Balanço
        balanco.to_excel(
            writer, sheet_name="Balanço",
            index=False, header=False, startrow=1)
        worksheet = writer.sheets["Balanço"]

        for i, val in zip(range(10), [8, 10, 14, 17, 12, 11, 10, 10, 8, 30]):
            col = chr(65 + i)
            worksheet.set_column(f"{col}:{col}", val)

        rows, columns = balanco.shape
        worksheet.add_table(0, 0, rows, columns - 1, {
            'columns': [{'header': column} for column in balanco.columns],
            'name': 'balanço'
        })

        # PPKs_ProdutoEstabelecimento
        worksheet = workbook.add_worksheet("PPKs_ProdutoEstabelecimento")
        A2_ = "ANCHORARRAY(A2)"
        B1_ = "ANCHORARRAY(B1)"

        worksheet.write_dynamic_array_formula("A2", f'=UNIQUE({est})')
        worksheet.write_dynamic_array_formula(
            "B1", f'=TRANSPOSE(UNIQUE({prd}))')
        worksheet.write_dynamic_array_formula(
            "B2",
            f'=IFERROR(AVERAGEIFS({ppk}, {est}, {A2_}, {prd}, {B1_}), NA())')
        for i in range(1, prd_count + 1):
            col = chr(65 + i)
            worksheet.conditional_format(f'{col}2:{col}{est_count + 1}', {
                'type': '3_color_scale',
                'min_color': '#63BE7B',
                'mid_color': '#FFEB84',
                'max_color': '#F8696B'
            })

        # 3Col_Mes
        worksheet = workbook.add_worksheet("3Col_Mes")
        worksheet.write_dynamic_array_formula(
            "A1", '=balanço[[#All], [Data]:[Média Preço]]')
        worksheet.set_column("C:C", 11)
        return


def check_reports():
    pr = {}

    for file in listdir(CFG.data):
        pr[file] = [0, 0, 0, 0, 0, 0, 0]
        if not file.endswith(".csv"):
            continue
        df = pd.read_csv(join(CFG.home, f"data/{file}"))
        if df.empty:
            continue
        if "TESTE" in df.loc[0, "Estabelecimento"]:
            continue

        for _, row in df.iterrows():
            if not isinstance(row["Nome"], str):
                pr[file][0] += 1
            if not isinstance(row["Data"], str):
                pr[file][1] += 1
            if not isinstance(row["Estabelecimento"], str):
                pr[file][2] += 1
            if not isinstance(row["Preço"], (int, float)) or np.isnan(
                row["Preço"]
            ):
                pr[file][5] += 1
            if not isinstance(row["Quantidade"], (int, float)):
                pr[file][6] += 1

            if not any(row["Produto"] == v for v in CFG.products):
                pr[file][3] += 1

            brands = load_raw_brands(row["Produto"])
            if brands is not None:
                if not any(row["Marca"] == v for v in brands):
                    pr[file][4] += 1

    headers = [
        "Nome", "Data", "Estabelecimento",
        "Produto", "Marca", "Preço", "Quantidade"]
    df = pd.DataFrame(pr).transpose()
    df = df[~(df == 0).all(axis=1)]
    df = df.set_axis(headers, axis=1)
    df = df.replace(0, "-")
    return df


def path_map(show=True):
    fig = go.Figure()
    names = {}
    estabs = {}
    dates = {}
    path = CFG.data_obs
    ests = pd.read_csv(join(CFG.home, "config/estabelecimentos.csv"))
    ests["Estabelecimento"] = ests["Estabelecimento"].str.split(" ").str[0]
    files = listdir(path)[::-1]
    for i in files:
        date = i.split("|")[0]
        if not date[0].isdigit():
            continue
        dates.setdefault(date, [])
        names.setdefault(date, set())
        estabs.setdefault(date, set())

        with open(join(path, i), "r") as file:
            lines = file.readlines()
            if not any("localização" in line for line in lines):
                continue

            rows = lines[next(
                i for i, v
                in enumerate(lines) if "localização" in v) + 1:]
            processedRow = []
            for row in rows:
                time, coords = row.split(":")
                lat, lon = coords.split(",")
                processedRow.append((int(time), float(lat), float(lon)))
            locDf = pd.DataFrame(
                processedRow, columns=["time", "Latitude", "Longitude"])
            locDf['time'] = pd.to_datetime(
                locDf['time'], unit='ms').dt.strftime('%H:%M')
            dates[date].append(locDf)

        names[date].add(i)
        estabs[date].add(i.split("|")[3].split(" ")[0].strip())

    for i in list(dates.keys()):
        if len(dates[i]) == 0:
            del dates[i]
            continue

    traces = []

    for k in dates.keys():
        name = list(names[k])
        estab = list(estabs[k])
        data = dates[k]
        df = ests.copy()

        # Split the data based on which establishments appear in the files
        condition = df['Estabelecimento'].apply(
            lambda x: any(est == x for est in estab))
        important = df[condition]
        rest = df[~condition]

        fig.add_trace(go.Scattermapbox(
            lat=rest.Latitude, lon=rest.Longitude,
            textposition="bottom center", mode='markers+text',
            textfont=dict(size=10, color="black"),
            marker=go.scattermapbox.Marker(size=10),
            text=rest.Estabelecimento, name='Estabs.'))
        fig.add_trace(go.Scattermapbox(
            lat=important.Latitude, lon=important.Longitude,
            textposition="bottom center", mode='markers+text',
            textfont=dict(size=10, color="black"),
            marker=go.scattermapbox.Marker(size=20),
            text=important.Estabelecimento, name='Objetivos'))
        traces.extend([k, k])

        # Add the data from the files (the movement of the collectors)
        for (i, d), name in zip(enumerate(data), name):
            traces.append(k)
            fig.add_trace(go.Scattermapbox(
                lat=d.Latitude, lon=d.Longitude,
                text=d.time, mode='lines+markers+text', textfont=dict(size=15),
                marker=dict(size=10), line=dict(width=3),
                name=f'{i+1}: {name.split("|")[3].split(" ")[0].strip()}'))

    border = 0.015
    fig.update_layout(
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
        margin={"r": 0, "t": 35, "l": 0, "b": 0},
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=df.Latitude.mean(), lon=df.Longitude.mean()),
            bounds=dict(
                west=df.Longitude.min() - border,
                east=df.Longitude.max() + border,
                south=df.Latitude.min() - border,
                north=df.Latitude.max() + border - 0.01)),
    )

    fig.update_layout(updatemenus=[
        dict(
            buttons=list([dict(
                args=[
                    {"visible": [v == date for v in traces]},
                    {"title": (
                        f"Movimentação dos coletores no dia {date}, "
                        f"{set(n.split("|")[2].strip() for n in names[date])}"
                    )}
                ],
                label=date, method="update")
                for i, date in enumerate(dates.keys())]),
            showactive=True, y=1, x=0, yanchor='top', xanchor='left',
        )
    ])
    fig.update_traces(visible=False)
    fig.data[0].visible = True
    for trace in fig.data[1:]:
        if "Estab" in trace.name:
            break
        trace.visible = True

    config = {'toImageButtonOptions': {
        'format': 'png', 'filename': f'Mov {date}, {names}', 'scale': 2}}
    if show:
        fig.show(config=config)
    else:
        return fig


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on the Earth's surface.

    Parameters:
    lat1, lon1: Latitude and Longitude of point 1 (in decimal degrees)
    lat2, lon2: Latitude and Longitude of point 2 (in decimal degrees)

    Returns:
    Distance in meters
    """
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    # Radius of the Earth in meters
    R = 6371000

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences in coordinates
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2 +
        math.cos(lat1_rad) * math.cos(lat2_rad) *
        math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in meters
    distance = R * c
    return distance
