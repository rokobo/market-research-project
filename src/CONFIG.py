from os.path import dirname
from types import SimpleNamespace


CFG = SimpleNamespace(**dict(
    home=dirname(dirname(__file__)),
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
))
