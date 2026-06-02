from products_to_csv import make_page_csv, make_table_csv
import argparse


def main():
    
    parser = argparse.ArgumentParser(description='This is a command line tool for parsing the tables on the Crafting page of the Coral Island fandom wiki and converting them to csv files.')

    subparsers = parser.add_subparsers(dest='command', help='AVAILABLE COMMANDS')

    # Single argument commands
    subparsers.add_parser('list-categories', help='Display list of available categories to choose from')
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


if __name__ == '__main__':
    main()