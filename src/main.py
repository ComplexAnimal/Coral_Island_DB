from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os


# Different columns required for different tables. Artisan equipment, Resource equipment,
# and Item producers all use Product, Ingredients, Produces, and Unlock.
# All other tables use only Product, Ingredients, and Unlock.
# Method to consider: Using adaptable url in format "coralisland.fandom.com/wiki/Crafting#{category}"
# Also maybe possible: Using if/then statements to check for the "Produces" column at time of data extraction.

# Something to watch out for: All tables contain a first column of checkboxes, which should be excluded for my purposes.


with sync_playwright() as p:
    browser = p.firefox.launch(headless=False, slow_mo=500)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    )
    page = context.new_page()

    page.goto("https://coralisland.fandom.com/wiki/Crafting", timeout=120000)
    page.wait_for_selector("table.article-table")
    html = page.content()

    browser.close()


soup = BeautifulSoup(html, "html.parser")
main_tag = soup.find("main")
if main_tag:
    pretty_html = main_tag.prettify()

script_dir = os.path.dirname(os.path.abspath(__file__))
dest_path = os.path.join(script_dir, "..", "tmp", "html.txt")

os.makedirs(os.path.dirname(dest_path), exist_ok=True)
with open(dest_path, "w", encoding="utf-8") as f:
    f.write(pretty_html)

'''
page_title = soup.find("h1", id="firstHeading")
if page_title:
    print(f"Success! Found page title: {page_title.text.strip()}")

tables = soup.find_all("table", class_="article-table")
print(f"Found {len(tables)} crafting tables.")

if tables:
    rows = tables[0].find_all("tr")
    if rows:
        header = rows.pop(0)
        first_entry = rows.pop(0)
        print(f"""First table title, header, and first entry:
{header.text.strip()}
{first_entry.text.strip()}""")
'''