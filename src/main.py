from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

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
page_title = soup.find("h1", id="firstHeading")
if page_title:
    print(f"Success! Found page title: {page_title.text.strip()}")

tables = soup.find_all("table", class_="article-table")
print(f"Found {len(tables)} crafting tables.")

if tables:
    first_row = tables[0].find("tr")
    if first_row:
        print(f"First table header/row: {first_row.text.strip()}")