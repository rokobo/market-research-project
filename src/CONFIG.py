from os.path import dirname, join
from types import SimpleNamespace
import pandas as pd


CFG = SimpleNamespace(**dict(
    home=dirname(dirname(__file__)),
    data_obs=join(dirname(dirname(__file__)), "data_obs"),
    data_path=join(dirname(dirname(__file__)), "data"),
    images=join(dirname(dirname(__file__)), "images"),
    products=[
        "acucar", "arroz", "cafe", "farinha", "feijao", "leite", "manteiga",
        "soja", "banana", "batata", "tomate", "carne", "pao"],
    quantities={
        'cafe': 0.5, 'arroz': 5, 'manteiga': 0.2, 'soja': 0.9},
    product_rows={
        "acucar": 2, "arroz": 4, "cafe": 4, "farinha": 3, "feijao": 4,
        "leite": 4, "manteiga": 4, "soja": 2, "banana": 2, "batata": 1,
        "tomate": 1, "carne": 1, "pao": 1},
    fields=["brand", "price", "quantity", "obs"],
    geo_length=100
))

COORDINATES = pd.read_csv(
    join(CFG.home, "config/estabelecimentos.csv")
).set_index("Estabelecimento").transpose().to_dict()
