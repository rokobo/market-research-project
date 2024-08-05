"""Tools for the pages."""

from os.path import join, exists
from os import makedirs, listdir
from send2trash import send2trash
import pandas as pd
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


def load_images() -> dict[str, str]:
    icons = {}
    for file in listdir(CFG.images):
        if not file.endswith(".svg"):
            continue
        name = file.split(".")[0].strip()
        with open(join(CFG.images, file), "r") as file:
            svg_data = file.read()
        icons[name] = svg_data
    return icons


def check_folder(path):
    if not exists(path):
        makedirs(path, exist_ok=True)


def save_products(
    product_data, info, obs: Optional[str],
    position: Optional[dict[str, Any]], geo_hist: Optional[list], test=False
):
    check_folder("data")
    check_folder("data_obs")
    rows = []

    for product, prod_name in zip(product_data, CFG.products):
        size = len(product[1])
        product = [
            col if len(col) == size
            else col + ([None] * (size - len(col)))
            for col in product]
        for row in list(zip(*product)):
            data = [prod_name]
            data.extend(row[:-1])
            if not isinstance(data[3], (float, int)):
                if prod_name in CFG.quantities:
                    quantidade = CFG.quantities[prod_name]
                else:
                    quantidade = 1
                data[3] = quantidade
            rows.append(data)

    df = pd.DataFrame(
        rows, columns=["Produto", "Marca", "Preço", "Quantidade"])
    df["Nome"] = info[0]
    df["Data"] = info[1]
    df["Estabelecimento"] = info[2].split(" ")[0]
    df = df[[
        "Nome", "Data", "Estabelecimento", "Produto",
        "Marca", "Preço", "Quantidade"]]
    if test:
        return df
    file_name = f"{info[1]}|{int(time.time())}|{info[0]}|{info[2]}"

    if isinstance(position, dict):
        if "lat" in position:
            file_name += f"|{position["lat"]}"
        if "lon" in position:
            file_name += f"|{position["lon"]}"
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
    two_months_ago = current_date - relativedelta(months=3)
    scheduled_delete = []
    for file in listdir(join(CFG.home, "data")):
        if not file.endswith(".csv"):
            continue
        year, month, day = file.split("|")[0].split("-")
        file_datetime = datetime(int(year), int(month), int(day))
        if file_datetime < two_months_ago:
            scheduled_delete.append(file)

    if scheduled_delete == []:
        print("No old files to delete")
        return

    print("Old files to delete:\n", "\n".join(scheduled_delete))

    for file in scheduled_delete:
        send2trash(join(CFG.home, f"data/{file}"))
    print("Old files deleted")


def aggregate_reports(date):
    # Collect all reports into a single dataframe
    reports = []
    check_folder(join(CFG.home, "data_agg"))
    assert len(date[0]) == 4, date
    assert len(date[1]) == 2, date

    for file in listdir(join(CFG.home, "data")):
        if not file.endswith(".csv"):
            continue
        file_date = file.split("|")[0].split("-")
        if file_date[1] != date[1]:
            continue

        df = pd.read_csv(join(CFG.home, f"data/{file}"))
        if df.empty:
            continue
        if "TESTE" in df.loc[0, "Estabelecimento"]:
            continue
        reports.append(df)

    if reports == []:
        print("No valid reports found")
        return
    print("Number of reports: ", len(reports))

    coleta_mes = pd.concat(reports)
    coleta_mes.Marca = coleta_mes.Marca.fillna("")
    coleta_mes["PPK"] = [
        f"=F{idx}/G{idx}" for idx in range(2, 2 + coleta_mes.shape[0])]

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
        "Produto": CFG.products[i-2],
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
