from html_to_products import parse_page, parse_table, rows_to_products, row_to_product
from html_to_products import Product, Crafter, Ingredient, categories
import csv, os


def make_page_csv():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_path = os.path.join(script_dir, '..', 'csvs', 'all_categories_db.csv')

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, 'w', newline='') as f:
        writer = csv.writer(f)

        prod_dict = parse_page()

        for table in prod_dict:

            for item in prod_dict[table]:
                print(item)

                if isinstance(item, (Product, Crafter)):
                    vals = item.convert_to_list()
                else:
                    vals = item

                writer.writerow(vals)

    html_path = os.path.join(script_dir, '..', 'tmp', 'html.txt')

    if os.path.exists(html_path):
        os.remove(html_path)


def make_table_csv(category):
    file_name = category.lower().replace(' ', '_') + '_db.csv'
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_path = os.path.join(script_dir, '..', 'csvs', file_name)

    rows = parse_table(category)
    prod_list = rows_to_products(rows)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, 'w', newline='') as f:
        writer = csv.writer(f)
        
        for item in prod_list:
            print(item)

            if isinstance(item, (Product, Crafter)):
                vals = item.convert_to_list()
            else:
                vals = item

            writer.writerow(vals)
            
    html_path = os.path.join(script_dir, '..', 'tmp', 'html.txt')

    if os.path.exists(html_path):
        os.remove(html_path)