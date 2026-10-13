import pytest
import allure
from faker import Faker
from playwright.sync_api import sync_playwright, Page
from tests.test_login_page import TestLoginPage


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--firefox", action="store_true", default=False, help="Использовать браузер Mozilla Firefox")
    parser.addoption("--safari", action="store_true", default=False, help="Использовать браузер Apple Safari")
    parser.addoption("--headless", action="store_true", default=False, help="Запуск в фоновом режиме")
    parser.addoption("--disable-images", action="store_true", default=False, help="Отключить картинки")
    parser.addoption("--screenshot-every-time", action="store_true", default=False, help="Делать частые скриншоты")
    parser.addoption("--wait-for-load", action="store_true", default=False, help="Дожидаться загрузки ресурсов")


@pytest.fixture
def browser_page(request: pytest.FixtureRequest) -> Page:
    firefox = request.config.getoption("--firefox")
    safari = request.config.getoption("--safari")
    headless = request.config.getoption("--headless")
    images = not request.config.getoption("--disable-images")
    screenshot_every_time = request.config.getoption("--screenshot-every-time")
    wait_for_load = request.config.getoption("--wait-for-load")

    if safari:
        browser_name = "Apple Safari"
    elif firefox:
        browser_name = "Mozilla Firefox"
    else:
        browser_name = "Google Chrome"

    playwright = sync_playwright().start()
    args = []

    if not firefox and not safari:
        args.append("--disable-blink-features=AutomationControlled")

    if headless and not firefox and not safari:
        args.append("--no-sandbox")
        args.append("--disable-dev-shm-usage")
        args.append("--disable-gpu")

    if safari:
        browser = playwright.webkit.launch(headless=headless, args=args)
    elif firefox:
        browser = playwright.firefox.launch(headless=headless, args=args)
    else:
        browser = playwright.chromium.launch(headless=headless, args=args)

    context = browser.new_context(extra_http_headers={"Accept-Encoding": "gzip, deflate"} if not images else {})

    if not images:
        context.route("**/*.{png,jpg,jpeg,gif,svg,webp}", lambda route: route.abort())

    print(f"\nЗапускается браузер {browser_name}...")
    page = context.new_page()
    page.set_viewport_size({"width": 1500, "height": 900})

    if screenshot_every_time:
        page.config = {"screenshot_every_time": True}
    else:
        page.config = {"screenshot_every_time": False}

    if wait_for_load:
        page.config["wait_for_load"] = True
    else:
        page.config["wait_for_load"] = False

    print("\nПроводятся тесты...")

    yield page
    print(f"\nБраузер {browser_name} закрывается...")
    browser.close()
    playwright.stop()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    test = outcome.get_result()

    if test.failed:
        browser_page = item.funcargs.get("browser_page")

        if browser_page:
            screenshot = browser_page.screenshot()
            allure.attach(screenshot, attachment_type=allure.attachment_type.PNG, name="Скриншот")


@pytest.fixture
def fake():
    return Faker()


@pytest.fixture
@allure.title("Регистрация нового пользователя")
def new_user_registration(browser_page, fake):
    test_suite = TestLoginPage()
    test_suite.test_new_user_registration(browser_page, fake)
