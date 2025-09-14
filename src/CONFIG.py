from os.path import dirname, join, getmtime, exists
from os import listdir, makedirs
from types import SimpleNamespace
import pandas as pd
import time
import sqlite3 as sql


update_time = f"{int(time.time()):,}".replace(",", ".")
config_folder = join(dirname(dirname(__file__)), "config")
with sql.connect(join(config_folder, "products.db")) as db:
    config = pd.read_sql(
        """
        SELECT *
        FROM products
        WHERE "group" IS NOT NULL AND "group" != ""
        ORDER BY brand_row DESC, product ASC
        """,
        db
    )
config["split"] = config["split"].astype(bool)


def get_splits(split, product):
    if split:
        with sql.connect(join(config_folder, "marcas.db")) as db:
            return pd.read_sql(
                f"SELECT brand FROM {product}", db).values.flatten().tolist()
    return None


config["splits"] = config.apply(
    lambda row: get_splits(row["split"], row["product"]), axis=1)


config["expanded"] = config.apply(
    lambda row: [f"{row['excel_product']} {sub}" for sub in row["splits"]]
    if row["split"] and row["splits"] else [row["excel_product"]], axis=1)

config["group"] = config["group"].apply(lambda x: tuple(x.split(",")))

CFG = SimpleNamespace(**dict(
    config_folder=config_folder,
    home=dirname(dirname(__file__)),
    data_obs=join(dirname(dirname(__file__)), "data_obs"),
    data=join(dirname(dirname(__file__)), "data"),
    pages=join(dirname(dirname(__file__)), "src/pages"),
    data_agg=join(dirname(dirname(__file__)), "data_agg"),
    data_agg_csv=join(dirname(dirname(__file__)), "data_agg_csv"),
    images=join(dirname(dirname(__file__)), "images"),
    products=config["product"].values.tolist(),
    groups=config["group"].values.tolist(),
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
    report_timeout_months=3,
    max_rows=8
))


titles = config.set_index('product')[
    ['title', 'subtitle']].apply(list, axis=1).to_dict()

CFG.product_titles = {
    prd: f"{lbl[0]} - {quant[0]}{quant[1]} {f"({lbl[1]})" if lbl[1] else ""}"
    for (prd, lbl), (_, quant) in zip(titles.items(), CFG.quantities.items())
}
CFG.product_index = {prd: i for i, prd in enumerate(CFG.products)}

CFG.unique_groups = CFG.groups.copy()
CFG.unique_groups = list(set([i for sub in CFG.unique_groups for i in sub]))


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

with sql.connect(join(config_folder, "estabelecimentos.db")) as db:
    COORDINATES = pd.read_sql("SELECT * FROM estabelecimentos", db)
    COORDINATES = COORDINATES.to_dict(orient="records")
    COORDINATES = sorted(COORDINATES, key=lambda x: x["code"])


BOLD = {'fontWeight': 'bold'}
CENTER = {'textAlign': 'center'}
UNDERLINE = {'textDecoration': 'underline'}
