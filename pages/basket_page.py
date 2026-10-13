from playwright.sync_api import Page
from pages.base_page import BasePage


class BasketPage(BasePage):
    def __init__(self, page: Page, url_path: str = "/basket/"):
        super().__init__(page)
        self.url = self.url + url_path

    def open(self, url: str = "", page_name: str = "cтраницу корзины") -> None:
        super().open(url, page_name)
