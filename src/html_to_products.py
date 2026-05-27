from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

class Product:
    def __init__(self, name, ingredients, unlock):
        self.name = name
        self.ingredients = ingredients
        self.unlock = unlock

    