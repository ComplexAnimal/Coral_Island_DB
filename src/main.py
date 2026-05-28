from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import sys
import os
import copy
import re

# Different columns required for different tables. Artisan equipment, Resource equipment,
# and Item producers all use Product, Ingredients, Produces, and Unlock.
# All other tables use only Product, Ingredients, and Unlock.
# Method to consider: Using adaptable url in format "coralisland.fandom.com/wiki/Crafting#{category}"
# Also maybe possible: Using if/then statements to check for the "Produces" column at time of data extraction.

# Something to watch out for: All tables contain a first column of checkboxes, which should be excluded for my purposes.

def main():

    force_refresh = "--refresh" in sys.argv

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_path = os.path.join(script_dir, "..", "tmp", "html.txt")

    # Only run scraping/slicing/saving block if tmp/html.txt doesn't already exist
    if not os.path.exists(dest_path) or force_refresh:

        print("File not found, proceeding with scraping...")

        # Requests html from "https://coralisland.fandom.com/wiki/Crafting" and converts it to a bs4 object
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
            )
            page = context.new_page()
            page.route(re.compile(r"google|amazon-adsystem|doubleclick|fandom-prod-ads"), block_and_log)

            '''
            # --- AD BLOCKING START ---
            context.route("*adsafeprotected*", block_and_log)
            context.route("*amazon-adsystem*", block_and_log)
            context.route("*doubleclick*", block_and_log)
            context.route("*google-analytics*", block_and_log)
            context.route("*googlesyndication*", block_and_log)
            context.route("*quantserve*", block_and_log)
            # --- AD BLOCKING END ---
            '''
            
            page.goto("https://coralisland.fandom.com/wiki/Crafting", timeout=120000)
            page.wait_for_selector("table.article-table")
            html = page.content()

            browser.close()

        soup = BeautifulSoup(html, "html.parser")

        # Slices out relevant-to-project html (starting with first <h3> tag and ending inclusively with <table...id="tpt-13"> tag) and prettifies it.
        start_tag = None
        for h3 in soup.find_all("h3"):
            if h3.find("span", id="Storage"):
                start_tag = h3
                break

        end_tag = soup.find("table", id="tpt-13")

        wrapper = soup.new_tag("div")

        if start_tag and end_tag:
            curr = start_tag
            while curr and curr != end_tag:
                wrapper.append(copy.copy(curr))
                curr = curr.find_next_sibling()

            wrapper.append(copy.copy(end_tag))

        final_html = wrapper.prettify()

        # Saves relevant html as html.txt to avoid having to scrape website during certain testing.
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(final_html)

    # Otherwise reference html.txt for relevant testing.
    else:
        print("File already exists, skipping scraping.")


def block_and_log(route):
    print(f"Blocking: {route.request.url}")
    route.abort()


if __name__ == "__main__":
    main()