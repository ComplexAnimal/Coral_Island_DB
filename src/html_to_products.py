from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os, copy, re


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
-----------------------------------------------'''

    def convert_to_list(self):
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
-----------------------------------------------'''

    def convert_to_list(self):
        crafter_list = super().convert_to_list()
        crafter_list.insert(3, self.produces)
        return crafter_list


class Ingredient:
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity

    def __repr__(self):
        return f'''Name: {self.name}
 -- Qty: {self.quantity}'''


def parse_page():
    all_products = {}

    for category in categories:
        rows = parse_table(category)
        all_products[category] = rows_to_products(rows)

    return all_products


def parse_table(category):

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_path = os.path.join(script_dir, '..', 'tmp', 'html.txt')

    # Only run scraping/slicing/saving block if tmp/html.txt doesn't already exist
    if not os.path.exists(dest_path):

        print('File not found, proceeding with scraping...')

        # Requests html from "https://coralisland.fandom.com/wiki/Crafting" and converts it to a bs4 object
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
            )
            page = context.new_page()

            # Ad blocking
            page.route(re.compile(r'google|amazon-adsystem|doubleclick|fandom-prod-ads'), block_and_log)
            
            page.goto('https://coralisland.fandom.com/wiki/Crafting', timeout=120000)
            page.wait_for_selector('table.article-table')
            html = page.content()

            browser.close()

        soup = BeautifulSoup(html, 'html.parser')

        # Slices out relevant-to-project html (starting with first <h3> tag and ending inclusively with <table...id="tpt-13"> tag) and prettifies it.
        start_tag = None
        for h3 in soup.find_all('h3'):
            if h3.find('span', id='Storage'):
                start_tag = h3
                break

        end_tag = soup.find('table', id='tpt-13')

        wrapper = soup.new_tag('div')

        if start_tag and end_tag:
            curr = start_tag
            while curr and curr != end_tag:
                wrapper.append(copy.copy(curr))
                curr = curr.find_next_sibling()

            wrapper.append(copy.copy(end_tag))

        final_html = wrapper.prettify()

        # Saves relevant html as html.txt to avoid having to scrape website each time parse_table called.
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(final_html)

    # Otherwise reference html.txt for relevant testing.
    else:
        print('File already exists, skipping scraping.')

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'r') as f:
        final_html = f.read()

    soup = BeautifulSoup(final_html, "html.parser")
    table_id = categories[category]

    table = soup.find("table", id=table_id)
    rows = table.find_all("tr")

    return rows


def block_and_log(route):
    print(f'Blocking: {route.request.url}')
    route.abort()


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

    # If row is a header, extract text from each cell, change product to name/yield, and return a list
    if cells[0].name == 'th':
        header = ['Name', 'Yield']

        for cell in cells[1:]:
            header_text = cell.get_text(strip=True)
            header.append(header_text)

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

            else:
                print("Error: No custom-icon-text found")

        else:
            print("Error: No icon-list found")

        # Optional "produces" column
        if len(cells) == 2:
            prod_col = cells.pop(0).find("div", class_="columntemplate")

            if prod_col is not None:
                produces = []

                icons = prod_col.find_all("span", class_="custom-icon")
                for icon in icons:
                    text_span = icon.find("span", class_="custom-icon-text")
                    if text_span:
                        produces.append(text_span.get_text(strip=True))

                direct_links = prod_col.find_all("a", recursive=False)
                for link in direct_links:
                    text = link.get_text(strip=True)
                    if text:
                        produces.append(text.capitalize())

                col_count += 1

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

            unlocks.extend(entries)

            col_count += 1
            
        else:
            print("Error: No unlock column found")

        if col_count == 5:
            return Crafter(name, _yield, ingredients, unlocks, produces)
        
        elif col_count == 4:
            return Product(name, _yield, ingredients, unlocks)
        
        else:
            print("Error: Incorrect number of columns")
            return