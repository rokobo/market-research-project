"""Tools for the pages."""

from os.path import dirname, join
import pandas as pd


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
            if brand == "-":
                brands.append({
                    "label": brand*20, "value": brand, "disabled": True
                })
            else:
                brands.append({
                    "label": brand, "value": brand
                })
    return brands


def validate_products(values) -> list[bool]:
    npt, npr, br, pr, qn, obs = values
    validations = []
    size = len(pr)

    validations.append([isinstance(brand, str) for brand in br])
    if npr != []:
        validations.append([
            (isinstance(price, (int, float)) and not no_price) or
            (no_price and price is None)
            for price, no_price in zip(pr, npr)
        ])
    else:
        validations.append([
            isinstance(price, (int, float))
            for price in pr
        ])

    if npt != []:
        validations.append([
            (isinstance(quantity, (int, float)) and no_pattern) or
            (not no_pattern and quantity is None)
            for quantity, no_pattern in zip(qn, npt)
        ])
    else:
        validations.append([
            isinstance(quantity, (int, float)) for quantity in qn])

    if obs != []:
        validations.append([True] * size)
    else:
        validations.append([])
    return validations


PRODUCTS = [
    "acucar", "arroz", "cafe", "farinha", "feijao", "leite", "manteiga",
    "soja", "banana", "batata", "tomate", "carne", "pao"]
QUANTIDADES = {
    'cafe': 0.5, 'arroz': 5, 'manteiga': 0.2, 'soja': 0.9
}

def save_products(product_data, info):
    rows = []
    for product, prod_name in zip(product_data, PRODUCTS):
        size = len(product[3])
        product = [
            col if len(col) == size
            else col + ([None] * (size - len(col)))
            for col in product]
        for row in list(zip(*product)):
            data = [prod_name]
            data.extend(row[2:5])
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
    df["PPK"] = df["Preço"] / df["Quantidade"]
    df = df[[
        "Nome", "Data", "Estabelecimento", "Produto",
        "Marca", "Preço", "Quantidade", "PPK"]]
    df.to_excel("text.xlsx", index=False)
    return
