import re
import time
from playwright.sync_api import Page, TimeoutError, Locator
from enums.wait_until import WaitUntil
from config import *


class Element:
    def __init__(self, page: Page, locator: str, timeout: float = TIMEOUT, waiting: WaitUntil = WaitUntil.PRESENT):
        self.page = page
        self.locator = locator
        self.timeout = timeout
        self.waiting = waiting

    def __repr__(self) -> str:
        return f"\nЭлемент(локатор: '{self.locator}', таймаут ожидания: {self.timeout} сек)"

    def get_elements(self) -> list[Locator]:
        start_time = time.time()

        try:
            self.page.wait_for_load_state("load", timeout=self.timeout * 1000)
        except TimeoutError:
            return []

        while time.time() - start_time < self.timeout:
            elements = self.page.locator(self.locator).all()

            if not elements:
                time.sleep(0.1)
                continue

            if self.waiting == WaitUntil.PRESENT:
                return elements
            elif self.waiting == WaitUntil.VISIBLE:
                if all(element.is_visible() for element in elements):
                    return elements
            elif self.waiting == WaitUntil.CLICKABLE:
                if all(element.is_visible() and element.is_enabled() for element in elements):
                    return elements

            time.sleep(0.1)

        return []

    def is_present(self) -> bool:
        return bool(self.get_elements())

    def is_clickable(self) -> bool:
        return self.is_present() and self.get_elements()[0].is_enabled()

    def is_not_clickable(self) -> bool:
        return self.is_present() and not self.get_elements()[0].is_enabled()

    def is_not_present(self) -> bool:
        return not self.is_present()

    def type_text(self, text: str) -> None:
        self.get_elements()[0].fill(text)

    def click(self) -> None:
        self.get_elements()[0].click()

    def press(self, keys_to_press: str) -> None:
        self.get_elements()[0].press(keys_to_press)

    def get_all_attributes(self) -> list[dict]:
        script = """
            elements => elements.map(element => {
                const attributes = {text: element.innerText};

                for (let attribute of element.attributes) attributes[attribute.name] = attribute.value;

                return attributes;
            })
            """

        if self.locator.startswith("/"):
            element = self.page.locator(f"xpath={self.locator}")
        else:
            element = self.page.locator(self.locator)

        if element.count() == 0:
            return []

        return element.evaluate_all(script)

    def get_attribute(self, attribute: str = "text") -> str:
        if attribute == "text":
            attribute_value = self.get_elements()[0].text_content()
        else:
            attribute_value = self.get_elements()[0].get_attribute(attribute)
            attribute_value = attribute_value if attribute_value else ""
            attribute_value = re.sub("<.*?>", "", attribute_value)

        return attribute_value

    def get_attribute_list(self, attribute: str = "text") -> list:
        if attribute == "text":
            attribute_list = [element.text_content() for element in self.get_elements()]
        else:
            attribute_list = []

            for element in self.get_elements():
                attribute_value = element.get_attribute(attribute)
                attribute_value = attribute_value if attribute_value else ""
                attribute_value = re.sub("<.*?>", "", attribute_value)
                attribute_list.append(attribute_value)

        return attribute_list

    def is_attribute_changed(self, attribute: str, old_value: str) -> bool:
        element = self.get_elements()[0]
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            current_value = element.get_attribute(attribute)

            if current_value is not None and current_value != old_value:
                return True

            time.sleep(0.1)

        return False

    def scroll_to(self) -> None:
        self.get_elements()[0].scroll_into_view_if_needed()
