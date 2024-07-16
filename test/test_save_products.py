"""Test dataframe generated by save_products()"""
import sys
from os.path import join, dirname
import pandas as pd


sys.path.append(join(dirname(dirname(__file__)), "src"))

from tools import save_products


PRODUCTS = [
    "acucar", "arroz", "cafe", "farinha", "feijao", "leite", "manteiga",
    "soja", "banana", "batata", "tomate", "carne", "pao"]



def test_one_line() -> None:
    """"Dataframes with one line."""
    for i, product in zip(range(len(PRODUCTS)), PRODUCTS):
        product_data = [([], [], [], [])] * 13
        product_data[i] = ([f"marca{i}"], [i], [i], [])
        info = ["name", "date", "establishment"]
        df1 = save_products(product_data, info, None, True)
        df2 = pd.DataFrame({
            'Nome': ["name"],
            'Data': ["date"],
            'Estabelecimento': ["establishment"],
            'Produto': [product],
            'Marca': [f"marca{i}"],
            'Preço': [i],
            'Quantidade': [i]
        })
        assert df1.equals(df2)


def test_two_lines() -> None:
    """"Dataframes with one line."""
    product_data = [([], [], [], [])] * 13
    product_data[0] = (["marca"], [2], [3], [])
    product_data[1] = (["marca2"], [4], [5], [])
    info = ["name", "date", "establishment"]
    df1 = save_products(product_data, info, None, True)
    df2 = pd.DataFrame({
        'Nome': ["name"] * 2,
        'Data': ["date"] * 2,
        'Estabelecimento': ["establishment"] * 2,
        'Produto': ["acucar", "arroz"],
        'Marca': ["marca", "marca2"],
        'Preço': [2, 4],
        'Quantidade': [3, 5]
    })
    assert df1.equals(df2)
