def locator(css_or_xpath_locator: str) -> str:
    if css_or_xpath_locator.startswith("/"):
        return "xpath=" + css_or_xpath_locator
    else:
        return css_or_xpath_locator
