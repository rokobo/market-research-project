"""Tools for the pages."""

from os.path import dirname, join


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


def save_products(products, info):
    # TODO
    print(products)
    print(info)
    return
