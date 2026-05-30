from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


categories = {
    "Storage": "tpt-1", 
    "Farming": "tpt-2",
    "Ranching": "tpt-3",
    "Artisan equipment": "tpt-4",
    "Resource equipment": "tpt-5",
    "Item producers": "tpt-6",
    "Decor": "tpt-7",
    "Consumables": "tpt-8",
    "Baits": "tpt-9",
    "Traps": "tpt-10",
    "Decoys": "tpt-11",
    "Bombs": "tpt-12",
    "Miscellaneous": "tpt-13"
}

class Product:
    def __init__(self, category, name, png, _yield, ingredients, unlock):
        self.category = category
        self.name = name
        self.png = png
        self._yield = _yield
        self.ingredients = ingredients
        self.unlock = unlock

    def convert_ingredients(self):
        ingredients_list = [[ingredient.name, ingredient.quantity] for ingredient in self.ingredients]
        return [self.category, self.name, self.png, self._yield, ingredients_list, self.unlock]
    

class Ingredient:
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity


def parse_page(html):
    all_products = {}

    for category in categories:
        rows = parse_table(html, category)
        all_products[category] = rows

    print(all_products)
    return all_products


def parse_table(html, category):
    soup = BeautifulSoup(html, "html.parser")
    table_id = categories[category]

    table = soup.find("table", id=table_id)
    rows = table.find_all("tr")

    return rows

def rows_to_products(rows):
    products = []
    for row in rows:
        product = row_to_product(row)
        products.append(product)

    return products