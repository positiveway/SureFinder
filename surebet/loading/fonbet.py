import requests
import random
import json

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from surebet.betting.fonbet import get_urls
from surebet.loading import *

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

URL_JSON = 'https://www.fonbet.com/urls.json?'
URL_LINE = '/live/currentLine/en?'


def load(browser):
    browser.get(url)

    try:
        browser.find_element_by_css_selector(expand).click()

        browser.find_element_by_css_selector(expand_all).click()

        WebDriverWait(browser, 10).until(ec.invisibility_of_element_located((By.CSS_SELECTOR, expand_all)))
    except NoSuchElementException:
        handle_loading_err(browser, name)

    log_loaded(name)


def load_events(browser):
    browser.execute_script(expand_remain)

    try:
        result = browser.find_element_by_css_selector(node).get_attribute("outerHTML")
    except NoSuchElementException:
        handle_loading_err(browser, name)
    else:
        log_loaded_events(name)
        return result


def load_events_json():
    urls_line = get_urls()['line']
    url_req_line = 'https://' + random.choice(urls_line)[2:] + URL_LINE + str(random.uniform(0, 1))

    r_line = requests.get(url_req_line, headers=browser_headers)
    check_status(r_line.status_code)

    try:
        result = json.loads(r_line.text)
    except json.JSONDecodeError:
        raise LoadException('Loaded invalid json for {}'.format(name))

    log_loaded(name + ' line json')
    return result
