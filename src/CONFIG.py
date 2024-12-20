from os.path import dirname, join, getmtime, exists
from os import listdir, makedirs
from types import SimpleNamespace
import pandas as pd
import time


update_time = f"{int(time.time()):,}".replace(",", ".")

CFG = SimpleNamespace(**dict(
    home=dirname(dirname(__file__)),
    data_obs=join(dirname(dirname(__file__)), "data_obs"),
    data=join(dirname(dirname(__file__)), "data"),
    data_agg=join(dirname(dirname(__file__)), "data_agg"),
    data_agg_csv=join(dirname(dirname(__file__)), "data_agg_csv"),
    images=join(dirname(dirname(__file__)), "images"),
    products=[
        "acucar", "arroz", "cafe", "farinha", "feijao", "leite", "manteiga",
        "soja", "banana", "batata", "tomate", "carne", "pao"],
    excel_products=[
        "Açúcar", "Arroz", "Café", "Farinha", "Feijão", "Leite", "Manteiga",
        "Óleo", "Banana Prata", "Banana Nanica", "Batata", "Tomate",
        "Carne", "Pão"],
    quantities={
        "acucar": [1, "kg"], "arroz": [5, "kg"], "cafe": [0.5, "kg"],
        "farinha": [1, "kg"], "feijao": [1, "kg"], "leite": [1, "L"],
        "manteiga": [0.2, "kg"], "soja": [0.9, "L"], "banana": [1, "kg"],
        "batata": [1, "kg"], "tomate": [1, "kg"], "carne": [1, "kg"],
        "pao": [1, "kg"]},
    product_rows={
        "acucar": 2, "arroz": 4, "cafe": 4, "farinha": 3, "feijao": 4,
        "leite": 4, "manteiga": 4, "soja": 2, "banana": 2, "batata": 1,
        "tomate": 1, "carne": 1, "pao": 1},
    fields=["brand", "price", "quantity"],
    field_names=["Marca", "Preço", "Quantidade"],
    product_fields={
        "acucar": [1, 1, 1], "arroz": [1, 1, 1], "cafe": [1, 1, 1],
        "farinha": [1, 1, 1], "feijao": [1, 1, 1], "leite": [1, 1, 1],
        "manteiga": [1, 1, 1], "soja": [1, 1, 1], "banana": [1, 1, 1],
        "batata": [0, 1, 1], "tomate": [0, 1, 1], "carne": [0, 1, 1],
        "pao": [0, 1, 1]},
    geo_length=100,
    expected_storage=[
        "geo-history", "geo-history-timestamp",
        "coordinates", "coordinates-timestamp",
        "files-hash", "files-hash-timestamp",
        "info-data", "info-data-timestamp",
        "config", "config-timestamp",
        "files-data", "files-data-timestamp",
        "grid-data", "grid-data-timestamp",
    ],
    report_timeout_months=3
))

titles = {
    "acucar": ["Açúcar", ""], "arroz": ["Arroz", ""], "cafe": ["Café", ""],
    "farinha": ["Farinha", ""], "feijao": ["Feijão", ""],
    "leite": ["Leite", ""], "manteiga": ["Manteiga", ""],
    "soja": ["Óleo", " (de soja)"], "banana": ["Banana", " (Nanica e Prata)"],
    "batata": ["Batata", " (mais barata)"],
    "tomate": ["Tomate", " (mais barato)"],
    "carne": ["Carne", " (Coxão Mole)"],
    "pao": ["Pão", " (Francês)"]}

CFG.product_titles = {
    prd: f"{lbl[0]} - {quant[0]}{quant[1]}{lbl[1]}"
    for (prd, lbl), (_, quant) in zip(titles.items(), CFG.quantities.items())
}
CFG.product_index = {prd: i for i, prd in enumerate(CFG.products)}

if not exists(CFG.data_agg_csv):
    makedirs(CFG.data_agg_csv, exist_ok=True)
CFG.csv_timestamps = {
    file[0:7]: int(getmtime(join(CFG.data_agg_csv, file)))
    for file in listdir(CFG.data_agg_csv)
}
CFG.version = update_time

assert len(CFG.products) == len(CFG.product_rows)
assert len(CFG.products) == len(CFG.product_fields)
assert len(CFG.products) == len(CFG.quantities)
assert len(CFG.products) == len(CFG.product_titles)

assert set(CFG.product_rows.keys()) == set(CFG.products)
assert set(CFG.product_fields.keys()) == set(CFG.products)
assert set(CFG.quantities.keys()) == set(CFG.products)
assert set(CFG.product_titles.keys()) == set(CFG.products)

COORDINATES = pd.read_csv(
    join(CFG.home, "config/estabelecimentos.csv")
).set_index("Estabelecimento").transpose().to_dict()
COORDINATES["version"] = update_time

ICONS = {}
for file in listdir(CFG.images):
    if not file.endswith(".svg"):
        continue
    name = file.split(".")[0].strip()
    if name not in CFG.products:
        continue
    with open(join(CFG.images, file), "r") as file:
        svg_data = file.read()
    ICONS[name] = svg_data

assert len(CFG.products) == len(ICONS)
assert set(ICONS.keys()) == set(CFG.products)


BOLD = {'fontWeight': 'bold'}
CENTER = {'textAlign': 'center'}
UNDERLINE = {'textDecoration': 'underline'}
