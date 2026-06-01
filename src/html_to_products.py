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
    def __init__(self, name, _yield, ingredients, unlocks):
        self.name = name
        self._yield = _yield
        self.ingredients = ingredients
        self.unlocks = unlocks

    def __repr__(self):
        return f'''
------------------- PRODUCT -------------------
Name: {self.name}
Yield: {self._yield}
Ingredients:\n - {"\n - ".join(str(i) for i in self.ingredients)}
Unlock Condition(s):\n > {"\n > ".join(self.unlocks)}
-----------------------------------------------
'''

    def convert_ingredients(self):
        ingredients_list = [[ingredient.name, ingredient.quantity] for ingredient in self.ingredients]
        return [self.name, self._yield, ingredients_list, self.unlocks]
    

class Crafter(Product):
    def __init__(self, name, _yield, ingredients, unlocks, produces):
        super().__init__(name, _yield, ingredients, unlocks)
        self.produces = produces

    def __repr__(self):
        return f'''
------------------- PRODUCT -------------------
Name: {self.name}
Yield: {self._yield}
Ingredients:\n - {"\n - ".join(str(i) for i in self.ingredients)}
Produces:\n = {"\n = ".join(self.produces)}
Unlock Condition(s):\n > {"\n > ".join(self.unlocks)}
-----------------------------------------------
'''

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
        return f'''Name: {self.name}
 -- Qty: {self.quantity}'''


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

    for product in products:
        print(product)
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

    # Otherwise, extract values from each cell and modify as necessary before creating and returning list
    else:
        col_count = 0

        # Name and _yield
        col_1 = cells.pop(0)
        col_1_text = col_1.get_text(strip=True)
        items = re.split(r'[^\w\s]\s+', col_1_text)
        name, _yield = items

        col_count += 2
        print(f'\nProduct name: {name}\nyield: {_yield}')

        # Ingredients
        ing_col = cells.pop(0).find("span", class_="icon-list")
        if ing_col is not None:
            ing_list = ing_col.find_all("span", class_="custom-icon-text")

            if ing_list is not None:
                ingredients = []

                for ing in ing_list:
                    ing_text = ing.get_text(strip=True)
                    ing_items = re.split(r'[^\w\s]\s?', ing_text)
                    ing_name, ing_quant = ing_items
                    ingredients.append(Ingredient(ing_name, ing_quant))

                col_count += 1

                print("Ingredients:")
                for item in ingredients:
                    print(item)

            else:
                print("Error: No custom-icon-text found")

        else:
            print("Error: No icon-list found")

        # Optional "produces" column
        if len(cells) == 2:
            prod_col = cells.pop(0).find("div", class_="columntemplate")

            if prod_col is not None:
                prod_list = prod_col.find_all("span", class_="custom-icon-text")
                produces = []
                
                if prod_list is not None:
                    for prod in prod_list:
                        prod_text = prod.get_text(strip=True)
                        produces.append(prod_text)

                    col_count += 1
                    print("Produces:")
                    for item in produces:
                        print(item)

                else:
                    print("Error: No custom-icon-text found")

            else:
                print("Error: No columntemplate found")

        # Unlock
        unlock_col = cells.pop(0)
        unlocks = []

        if unlock_col is not None:
            for noise in unlock_col.find_all("span", class_=["sort-value", "custom-icon-image"]):
                noise.decompose()

            raw_entries = list(unlock_col.stripped_strings)

            icon_containers = unlock_col.find_all("span", class_="custom-icon")
            direct_links = unlock_col.find_all("a", recursive=False)

            all_text = "".join(raw_entries)
            structured_text = "".join([i.get_text(strip=True) for i in icon_containers] +
                                      [l.get_text(strip=True) for l in direct_links])

            if (len(icon_containers) + len(direct_links)) > 1 and len(all_text) == len(structured_text):
                entries = raw_entries

            else:
                combined = " ".join(raw_entries).strip()
                entries = [combined] if combined else []

            entries = [e.replace('\xa0', ' ') for e in entries if e]

            print('ENTRIES:')
            for entry in entries:
                print(f'--- {entry}')

            unlocks.extend(entries)

            col_count += 1
            print("Unlock conditions:")
            for unlock in unlocks:
                print(unlock)
            
        else:
            print("Error: No unlock column found")

        if col_count == 5:
            print(f"column count: {col_count}")
            return Crafter(name, _yield, ingredients, unlocks, produces)
        
        elif col_count == 4:
            print(f"column count: {col_count}")
            return Product(name, _yield, ingredients, unlocks)
        
        else:
            print("Error: Incorrect number of columns")
            return