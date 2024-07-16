from os.path import dirname

HOME = dirname(dirname(__file__))
PRODUCTS = [
    "acucar", "arroz", "cafe", "farinha", "feijao", "leite", "manteiga",
    "soja", "banana", "batata", "tomate", "carne", "pao"]
QUANTITIES = {
    'cafe': 0.5, 'arroz': 5, 'manteiga': 0.2, 'soja': 0.9}
PRODUCT_ROWS = {
    "acucar": 3, "arroz": 3, "cafe": 3, "farinha": 3, "feijao": 3,
    "leite": 3, "manteiga": 3, "soja": 3, "banana": 2, "batata": 1,
    "tomate": 1, "carne": 1, "pao": 1}
FIELDS = ["brand", "price", "quantity", "obs"]
