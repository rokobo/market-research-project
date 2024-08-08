# flake8: noqa: E501
"""Test dataframe generated by save_products()"""
import sys
from os.path import join, dirname
from os import remove, listdir
import pandas as pd
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


sys.path.append(join(dirname(dirname(__file__)), "src"))

from tools import aggregate_reports, save_products, delete_old_reports
from CONFIG import CFG


def delete_data_files():
    for file in listdir(CFG.data_obs):
        remove(join(CFG.data_obs, file))
    for file in listdir(CFG.data):
        remove(join(CFG.data, file))


def test_one_line() -> None:
    """"Dataframes with one line."""
    for i, product in enumerate(CFG.products):
        product_data = [([], [], [], [])] * 13
        product_data[i] = ([f"marca{i}"], [i], [i], [])
        info = ["name", "date", "establishment"]
        df1 = save_products(product_data, info, None, None, None, True)
        df2 = pd.DataFrame({
            'Nome': ["name"],
            'Data': ["date"],
            'Estabelecimento': ["establishment"],
            'Produto': [product],
            'Marca': [f"marca{i}"],
            'Preço': [i],
            'Quantidade': [i]
        })
        assert df1 is not None
        assert df1.equals(df2)


def test_two_lines() -> None:
    """"Dataframes with one line."""
    product_data = [([], [], [], [])] * 13
    product_data[0] = (["marca"], [2], [3], [])
    product_data[1] = (["marca2"], [4], [5], [])
    info = ["name", "date", "establishment"]
    df1 = save_products(product_data, info, None, None, None, True)
    df2 = pd.DataFrame({
        'Nome': ["name"] * 2,
        'Data': ["date"] * 2,
        'Estabelecimento': ["establishment"] * 2,
        'Produto': ["acucar", "arroz"],
        'Marca': ["marca", "marca2"],
        'Preço': [2, 4],
        'Quantidade': [3, 5]
    })
    assert df1 is not None
    assert df1.equals(df2)


def test_banana_naming() -> None:
    delete_data_files()
    product_data = [([], [], [], [])] * 13
    product_data[0] = (["marca"], [2], [3], [])
    product_data[CFG.products.index("banana")] = (
        ["Nanica", "Prata"], [1, 2], [], [])
    info = ["name", "2024-01-01", "establishment"]
    save_products(product_data, info, None, None, None, False)
    df = aggregate_reports(["2024", "01"], True)
    assert df is not None
    mask = df['Produto'].str.contains("banana")
    assert len(df) == 3, df
    assert all(not val for val in df.loc[mask, 'Marca']), df.Marca.to_list()
    assert "banana nanica" in df.loc[mask, 'Produto'].to_list(), df.Produto.to_list()
    assert "banana prata" in df.loc[mask, 'Produto'].to_list(), df.Produto.to_list()
    delete_data_files()


def test_naming() -> None:
    delete_data_files()
    product_data = [([], [], [], [])] * 13
    info = ["name", "date", "establishment"]
    save_products(product_data, info, None, None, None)
    file_name = None

    for file in listdir(CFG.data):
        file_name = file
        break

    assert file_name
    fields = file_name.split("|")
    assert len(fields) == 4, fields
    assert fields[0] == info[1], fields
    assert abs(int(fields[1]) - int(time.time())) < 10, fields
    assert fields[2] == info[0], fields
    assert fields[3].replace(".csv", "") == info[2], fields
    delete_data_files()


def test_naming_coordinates() -> None:
    delete_data_files()
    product_data = [([], [], [], [])] * 13
    info = ["name", "date", "establishment"]
    save_products(product_data, info, None, {
        'lat': -22.895, 'lon': -47.0439, 'accuracy': 1, 'alt': None,
        'alt_accuracy': None, 'speed': None, 'heading': None}, None)
    file_name = None

    for file in listdir(CFG.data):
        file_name = file
        break

    assert file_name
    fields = file_name.split("|")
    assert len(fields) == 6, fields
    assert fields[0] == info[1], fields
    assert abs(int(fields[1]) - int(time.time())) < 10, fields
    assert fields[2] == info[0], fields
    assert fields[3] == info[2], fields
    assert fields[4] == "-22.895", fields
    assert fields[5].replace(".csv", "") == "-47.0439", fields
    delete_data_files()


def test_short_geo_history() -> None:
    delete_data_files()
    product_data = [([], [], [], [])] * 13
    info = ["name", "date", "establishment"]
    geo_hist = [[1, 2, 3], [4, 5, 6]]
    save_products(product_data, info, None, None, geo_hist)
    file_name = None

    for file in listdir(CFG.data_obs):
        file_name = join(CFG.data_obs, file)
        break

    assert file_name
    with open(file_name, 'r') as file:
        observations = file.readlines()

    assert "Sem observações" == observations[0].strip()
    assert "Histórico de geolocalização" == observations[2].strip()
    for i, obs in enumerate(observations[3:]):
        geo = geo_hist[i]
        assert obs.strip() == f"{geo[2]}: {geo[0]}, {geo[1]}"

    delete_data_files()


def test_longe_geo_history() -> None:
    delete_data_files()
    product_data = [([], [], [], [])] * 13
    info = ["name", "date", "establishment"]
    geo_hist = [[i, i+1, i+2] for i in range(100)]
    save_products(product_data, info, None, None, geo_hist)
    file_name = None

    for file in listdir(CFG.data_obs):
        file_name = join(CFG.data_obs, file)
        break

    assert file_name
    with open(file_name, 'r') as file:
        observations = file.readlines()

    assert "Sem observações" == observations[0].strip()
    assert "Histórico de geolocalização" == observations[2].strip()
    for i, obs in enumerate(observations[3:]):
        geo = geo_hist[i]
        assert obs.strip() == f"{geo[2]}: {geo[0]}, {geo[1]}"

    delete_data_files()


def test_delete_simple() -> None:
    delete_data_files()
    for i in range(10):
        product_data = [([], [], [], [])] * 13
        product_data[1] = ([f"marca{1}"], [1], [1], [])
        info = [f"name{i}", "2020-06-28", "establishment"]
        save_products(product_data, info, None, None, None)

    assert len(listdir(CFG.data)) == 10

    delete_old_reports()

    assert len(listdir(CFG.data)) == 0
    delete_data_files()


def test_delete_4_months() -> None:
    delete_data_files()
    for i in range(10):
        product_data = [([], [], [], [])] * 13
        product_data[1] = ([f"marca{1}"], [1], [1], [])
        info = [
            f"name{i}",
            (datetime.today()-relativedelta(months=4)).strftime('%Y-%m-%d'),
            "establishment"]
        save_products(product_data, info, None, None, None)

    assert len(listdir(CFG.data)) == 10

    delete_old_reports()

    assert len(listdir(CFG.data)) == 0
    delete_data_files()


def test_delete_multiple() -> None:
    delete_data_files()
    for i in range(1, 10):
        product_data = [([], [], [], [])] * 13
        product_data[1] = ([f"marca{1}"], [1], [1], [])
        info = [
            f"name{i}",
            (datetime.today()-relativedelta(months=6-i)).strftime('%Y-%m-%d'),
            "establishment"]
        save_products(product_data, info, None, None, None)

    assert len(listdir(CFG.data)) == 9

    delete_old_reports()

    assert len(listdir(CFG.data)) == 7
    for file in listdir(CFG.data):
        remove(join(CFG.data, file))
    delete_data_files()
