from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re


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
    def __init__(self, name, _yield, ingredients, unlock):
        self.name = name
        self._yield = _yield
        self.ingredients = ingredients
        self.unlock = unlock

    def convert_ingredients(self):
        ingredients_list = [[ingredient.name, ingredient.quantity] for ingredient in self.ingredients]
        return [self.name, self._yield, ingredients_list, self.unlock]
    

class Crafter(Product):
    def __init__(self, name, _yield, ingredients, unlock, produces):
        super().__init__(self, name, _yield, ingredients, unlock)
        self.produces = produces

    def convert_ingredients(self):
        return super().convert_ingredients()
    
    def add_produces(self):
        produces_added = self.convert_ingredients().insert(3, self.produces)
        return produces_added


class Ingredient:
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity

    def __repr__(self):
        return f'name: {self.name}, quantity: {self.quantity}'


def parse_page(html):
    all_products = {}

    for category in categories:
        rows = parse_table(html, category)
        all_products[category] = rows_to_products(rows)

    print(all_products)
    return all_products


def parse_table(html, category):
    soup = BeautifulSoup(html, "html.parser")
    table_id = categories[category]

    table = soup.find("table", id=table_id)
    print(f"Table found: '{table_id}'")                 # DELETE
    rows = table.find_all("tr")
    products = rows_to_products(rows)                   # DELETE

    return rows


def rows_to_products(rows):
    products = []
    for row in rows:
        product = row_to_product(row)
        products.append(product)

    return products


def row_to_product(row):
    cells = row.find_all(['td', 'th'])

    # First column is a progress tracker. Useless for the purpose of this program.
    checkbox = cells.pop(0)

    # If row is a header, extract text from each cell and return a list
    if cells[0].name == 'th':
        header = []

        for cell in cells:
            header_text = cell.get_text(strip=True)
            header.append(header_text)

        print(header)
        return header

    # Otherwise, extract values from each cell and modify as necessary before creating list
    else:
        # name and _yield
        col_1 = cells.pop(0)
        col_1_text = col_1.get_text(strip=True)
        items = re.split(r'[^\w\s]\s?', col_1_text)
        name, _yield = items
        print(f'Product name: {name}\nyield: {_yield}')

        # ingredients
        ing_col = cells.pop(0).find("span", class_="icon-list")
        ing_list = ing_col.find_all("span", class_="custom-icon-text")
        ingredients = []

        for ing in ing_list:
            ing_text = ing.get_text(strip=True)
            ing_items = re.split(r'[^\w\s]\s?', ing_text)
            ing_name, ing_quant = ing_items
            ingredients.append(Ingredient(ing_name, ing_quant))

        print("Ingredients:")
        for item in ingredients:
            print(item)

        # Optional produces column
        if len(cells) == 2:
            

        return