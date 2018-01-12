from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from surebet.loading import log_loaded, LoadException

name = "fonbet"

url = 'https://www.fonbet.com/live/?locale=en'
node = '#lineTable'

expand = '#lineTableHeaderButton'
expand_all = '#lineHeaderViewActionMenu > .popupMenuItem:nth-child(6)'
closed_event = 'span[style="display: inline-block;"].detailArrowClose'

expand_remain = """
nodes = document.querySelectorAll('span[style="display: inline-block;"].detailArrowClose')
for (cur_node = 0; cur_node < nodes.length; cur_node++) {
    nodes[cur_node].click()
}
"""


def load(browser):
    browser.get(url)

    try:
        browser.find_element_by_css_selector(expand).click()
    except NoSuchElementException:
        browser.get_screenshot_as_file("{}-error.png".format(name))
        raise LoadException("site is not responding")

    browser.find_element_by_css_selector(expand_all).click()

    WebDriverWait(browser, 10).until(ec.invisibility_of_element_located((By.CSS_SELECTOR, expand_all)))
    print("{}: loaded".format(name))


def load_events(browser):
    browser.execute_script(expand_remain)

    result = browser.find_element_by_css_selector(node).get_attribute("outerHTML")
    log_loaded(name)
    return result
