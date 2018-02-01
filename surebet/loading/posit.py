from json import load

from os import path
from random import choice, seed
from selenium.common.exceptions import NoSuchElementException

from surebet.loading import *

# TODO: replace by mock
# temporary generates random account
seed()
with open(path.join(package_dir, "accounts.json")) as file:
    accounts = load(file)
default_account = choice(accounts)

name = "positivebet"
url = "https://positivebet.com/en/user/login"

node = "#gridBets > table"


def load(browser, account=default_account):
    browser.get(url)

    try:
        browser.find_element_by_id("UserLogin_username").send_keys(account['login'])
        browser.find_element_by_id("UserLogin_password").send_keys(account['pass'])
        browser.find_element_by_id("UserLogin_rememberMe").click()
        browser.find_element_by_name("yt0").click()

        browser.find_element_by_link_text("Live bets").click()
        browser.find_element_by_link_text("Live bets").click()

        browser.find_element_by_name("yt1").click()
        browser.find_element_by_xpath("//select[@name='Bets[per_page]']/option[text()='30']").click()
    except NoSuchElementException:
        handle_loading_err(browser, name)

    log_loaded(name)


def load_events(browser):
    try:
        result = browser.find_element_by_css_selector(node).get_attribute("outerHTML")
    except NoSuchElementException:
        handle_loading_err(browser, name)
    else:
        log_loaded_events(name)
        return result
