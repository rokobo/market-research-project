"""Tools for the pages."""

from os.path import dirname, join, exists
from os import makedirs, listdir
import pandas as pd
from openpyxl import load_workbook
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


def save_products(product_data, info):
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
    df["Estabelecimento"] = info[2]
    df = df[[
        "Nome", "Data", "Estabelecimento", "Produto",
        "Marca", "Preço", "Quantidade"]]
    df.to_csv(f"data/{info[1]}|{int(time.time())}.csv", index=False)
    return
# save_products(d, info)
# workbook = load_workbook(f"{info[1]}|{info[0]}.xlsx")
# sheet = workbook.active
# for row in range(2, 15):  # Adjust the range based on DataFrame size
#     sheet[f'H{row}'] = f'=F{row} / G{row}'  # Example formula

# workbook.save(f"{info[1]}|{info[0]}.xlsx")
