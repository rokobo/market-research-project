"""Tools for the pages."""

from os.path import dirname, join, exists
from os import makedirs, listdir
import pandas as pd
import xlsxwriter
import time


HOME = dirname(dirname(__file__))


def load_establishments() -> list[dict[str, str]]:
    establishments = []
    with open(join(HOME, "config/estabelecimentos.txt"), 'r') as file:
        for line in file:
            est = line.strip()
            establishments.append({
                "label": est, "value": est
            })
    return establishments


def load_brands(product: str) -> list[dict[str, str]]:
    brands = []
    with open(join(HOME, f"config/marcas-{product}.txt"), 'r') as file:
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


def check_folder(path):
    if not exists(path):
        makedirs(path, exist_ok=True)


PRODUCTS = [
    "acucar", "arroz", "cafe", "farinha", "feijao", "leite", "manteiga",
    "soja", "banana", "batata", "tomate", "carne", "pao"]
QUANTIDADES = {
    'cafe': 0.5, 'arroz': 5, 'manteiga': 0.2, 'soja': 0.9
}


def save_products(product_data, info, test=False):
    check_folder("data")
    rows = []

    for product, prod_name in zip(product_data, PRODUCTS):
        size = len(product[1])
        product = [
            col if len(col) == size
            else col + ([None] * (size - len(col)))
            for col in product]
        for row in list(zip(*product)):
            data = [prod_name]
            data.extend(row[:-1])
            if not isinstance(data[3], (float, int)):
                if prod_name in QUANTIDADES:
                    quantidade = QUANTIDADES[prod_name]
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
    df.to_csv(
        f"data/{info[1]}|{int(time.time())}|{info[0]}.csv",
        index=False)
    return


def aggregate_reports(date=["2024", "06"]):
    # Collect all reports into a single dataframe
    reports = []
    check_folder("data_agg")

    for file in listdir("data"):
        file_date = file.split("|")[0].split("-")
        if file_date[1] != date[1]:
            continue

        df = pd.read_csv(f"data/{file}")
        if df.empty:
            continue
        reports.append(df)
    coleta_mes = pd.concat(reports)
    coleta_mes.Marca = coleta_mes.Marca.fillna("")
    coleta_mes["PPK"] = [
        f"=F{idx}/G{idx}" for idx in range(2, 2 + coleta_mes.shape[0])]

    # Create basic statistics for the reports
    ppk = "coleta_mes[PPK]"
    prd = "coleta_mes[Produto]"
    prc = "coleta_mes[Preço]"
    date_col = f"{date[0]}/{date[1]}"
    balanco = pd.DataFrame([{
        "Data": date_col,
        "Produto": PRODUCTS[i-2],
        "Média Preço": f"=ROUND(AVERAGEIFS({prc}, {prd}, B{i}), 3)",
        "Média PPK": f"=ROUND(AVERAGEIFS({ppk}, {prd}, B{i}), 3)",
        "Registros": f"=COUNTIF({prd}, B{i})",
        "Min PPK": f'=ROUND(MINIFS({ppk}, {prd}, B{i}), 3)',
        "Max PPK": f"=ROUND(MAXIFS({ppk}, {prd}, B{i}), 3)",
        # "Q1": f"=QUARTILE(IF({prd}=B{i}, {ppk}), 1)",
        # "Q2": f"=QUARTILE(IF({prd}=B{i}, {ppk}), 2)",
        # "Q3": f"=QUARTILE(IF({prd}=B{i}, {ppk}), 3)",
        "σ PPK": f"=SINGLE(ROUND(STDEV.P(IF({prd}=B{i}, {ppk})) , 3))",
        "Lista de preços outlier": (
            f'=TEXTJOIN(", ", TRUE, FILTER({prc}, ({prd}=B{i})'
            f' * (({ppk} < (D{i} - (H{i} * 3))) + '
            f'({ppk} > (D{i} + (H{i} * 3)))), "-"))'
        ),
        # "Outliers IQR":
    } for i in range(2, len(PRODUCTS) + 2)])

    # Save
    with pd.ExcelWriter(
        f"data_agg/{date[0]}_{date[1]}_Coleta.xlsx", engine="xlsxwriter",
        engine_kwargs={'options': {
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
                '=ABS(H2 - VLOOKUP(D2, Balanço!B:H, 3, FALSE)) '
                '> VLOOKUP(D2, Balanço!B:H, 7, FALSE)*3'),
            'format': workbook.add_format({
                'bg_color':   '#FFC7CE', 'font_color': '#9C0006'})
        })

        # Balanço
        balanco.to_excel(
            writer, sheet_name="Balanço",
            index=False, header=False, startrow=1)
        worksheet = writer.sheets["Balanço"]
        worksheet.set_column("B:B", 10)
        worksheet.set_column("C:C", 14)
        worksheet.set_column("D:D", 12)
        worksheet.set_column("E:E", 11)
        worksheet.set_column("F:F", 10)
        worksheet.set_column("G:G", 10)
        worksheet.set_column("I:I", 30)
        rows, columns = balanco.shape
        worksheet.add_table(0, 0, rows, columns - 1, {
            'columns': [{'header': column} for column in balanco.columns],
            'name': 'balanço'
        })

        # Balanço_ProdutoMarca
        worksheet = workbook.add_worksheet("Balanço_ProdutoMarca")
        for col, value in enumerate([
            "Data", "Produto", "Marca", "Preço", "Registros", "PPK"
        ]):
            worksheet.write(0, col, value)

        marca = "coleta_mes[Marca]"
        sro = "ANCHORARRAY(B2)"
        prod = "coleta_mes[Produto]"
        prd_mrc = "coleta_mes[[Produto]:[Marca]]"
        sqn = f"SEQUENCE(ROWS({sro}), 1)"

        worksheet.write_dynamic_array_formula("A2", (
            f'=VLOOKUP(INDEX({sro}, {sqn}, 1), balanço[[Data]:[Produto]], 1)'))
        worksheet.write_dynamic_array_formula("B2", (
            f'=UNIQUE(IF({prd_mrc}<>"", {prd_mrc}, '
            f'{prd_mrc} & ""), FALSE, FALSE)'))
        worksheet.write_dynamic_array_formula("D2", (
            '=ROUND(AVERAGEIFS(coleta_mes[Preço], '
            f'{prod}, INDEX({sro}, {sqn}, 1), '
            f'{marca}, INDEX({sro}, {sqn}, 2)), 3)'))
        worksheet.write_dynamic_array_formula("E2", (
            f'=COUNTIFS({prod}, INDEX({sro}, {sqn}, 1), '
            f'{marca}, INDEX({sro}, {sqn}, 2))'))
        worksheet.write_dynamic_array_formula("F2", (
            '=ROUND(AVERAGEIFS(coleta_mes[PPK], '
            f'{prod}, INDEX({sro}, {sqn}, 1), '
            f'{marca}, INDEX({sro}, {sqn}, 2)), 3)'))

        # 3Col_Mes
        worksheet = workbook.add_worksheet("3Col_Mes")
        worksheet.write_dynamic_array_formula(
            "A1", '=balanço[[#All], [Data]:[Média Preço]]')
        worksheet.set_column("C:C", 11)
