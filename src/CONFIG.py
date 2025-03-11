from os.path import dirname, join, getmtime, exists
from os import listdir, makedirs
from types import SimpleNamespace
import pandas as pd
import time
import sqlite3 as sql


update_time = f"{int(time.time()):,}".replace(",", ".")
config_folder = join(dirname(dirname(__file__)), "config")
with sql.connect(join(config_folder, "products.db")) as db:
    config = pd.read_sql("SELECT * FROM products", db)
config["split"] = config["split"].astype(bool)


def get_splits(split, product):
    file_path = join(config_folder, f"marcas-{product}.txt")
    if split:
        assert exists(file_path), f"Missing required file: {file_path}"
        with open(file_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    return None


config["splits"] = config.apply(
    lambda row: get_splits(row["split"], row["product"]), axis=1)

config["expanded"] = config.apply(
    lambda row: [f"{row['excel_product']} {sub}" for sub in row["splits"]]
    if row["split"] and row["splits"] else [row["excel_product"]], axis=1)

CFG = SimpleNamespace(**dict(
    home=dirname(dirname(__file__)),
    data_obs=join(dirname(dirname(__file__)), "data_obs"),
    data=join(dirname(dirname(__file__)), "data"),
    data_agg=join(dirname(dirname(__file__)), "data_agg"),
    data_agg_csv=join(dirname(dirname(__file__)), "data_agg_csv"),
    images=join(dirname(dirname(__file__)), "images"),
    products=config["product"].values,
    excel_products=config["expanded"].explode().tolist(),
    quantities=config.set_index('product')[
        ['quantity', 'quantity_unit']].apply(list, axis=1).to_dict(),
    product_rows=config.set_index('product')['product_rows'].to_dict(),
    product_splits=config.loc[config["split"], "product"].tolist(),
    fields=["brand", "price", "quantity"],
    field_names=["Marca", "Preço", "Quantidade"],
    product_fields=config.set_index('product')[
        ['brand_row', 'price_row', 'quantity_row']
    ].apply(list, axis=1).to_dict(),
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

titles = config.set_index('product')[
    ['title', 'subtitle']].apply(list, axis=1).to_dict()


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
