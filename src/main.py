from products_to_csv import make_page_csv, make_table_csv
import argparse, sys

# Add logic for arg parsing
# Add separate method calls for parsing one table vs the whole page

def main():
    # START ARG PARSING BLOCK
    """
    parser = argparse.ArgumentParser(description='This is a command line tool for parsing the tables on the Crafting page of the Coral Island fandom wiki and converting them to csv files.')

    subparsers = parser.add_subparsers(dest='command', help='AVAILABLE COMMANDS')

    # Single argument commands
    subparsers.add_parser('list-categories', help='Storage, Farming, Ranching, Artisan equipment,\nResource equipment, Item producers, Decor,\nConsumables, Baits, Traps, Decoys, Bombs,\nMiscellaneous')
    subparsers.add_parser('convert-page', help='Generates a csv file for every category')

    # Multiple argument commands
    comm_parse_table = subparsers.add_parser('convert-table', help='Generates a csv file for a single specified category')
    comm_parse_table.add_argument('category', type=str, help='Name of category')

    args = parser.parse_args()

    # Command list
    if args.command == 'help' or args.command is None:
        parser.print_help()
    elif args.command == 'list-categories':
        print('''
CATEGORIES: Storage, Farming, Ranching, Artisan equipment, Resource equipment, Item producers, Decor, Consumables, Baits, Traps, Decoys, Bombs, Miscellaneous''')
    elif args.command == 'convert-page':
        make_page_csv()
    elif args.command == 'convert-table':
        make_table_csv(args.category)
    """
    # END ARG PARSING BLOCK

    """
    force_refresh = '--refresh' in sys.argv

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_path = os.path.join(script_dir, '..', 'tmp', 'html.txt')

    # Only run scraping/slicing/saving block if tmp/html.txt doesn't already exist
    if not os.path.exists(dest_path) or force_refresh:

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

        # Saves relevant html as html.txt to avoid having to scrape website during certain testing.
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(final_html)

    # Otherwise reference html.txt for relevant testing.
    else:
        print('File already exists, skipping scraping.')

    with open(dest_path, 'r') as f:
        cached_html = f.read()

def block_and_log(route):
    print(f'Blocking: {route.request.url}')
    route.abort()
"""

make_page_csv()

if __name__ == '__main__':
    main()