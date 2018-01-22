from selenium.webdriver.common.keys import Keys
from surebet.loading import *


name = "positivebet"
url = "http://positivebet.com/en"


def log_in(browser, account):
    browser.get(url)
    browser.find_element_by_link_text("Login").send_keys(Keys.RETURN)
    browser.find_element_by_id("UserLogin_username").send_keys(account['login'])
    browser.find_element_by_id("UserLogin_password").send_keys(account['password'])
    browser.find_element_by_name("yt0").send_keys(Keys.RETURN)
    browser.find_element_by_link_text("Live bets").send_keys(Keys.RETURN)
    browser.find_element_by_link_text("Live bets").send_keys(Keys.RETURN)
    browser.find_element_by_name("yt1").send_keys(Keys.RETURN)
    browser.find_element_by_id("ddlPerPage").send_keys(Keys.RETURN)
    browser.find_element_by_xpath("//select[@name='Bets[per_page]']/option[text()='30']").click()
    log_loaded(name)


# log_in(webdriver.Chrome(), {'login' : "kolyan312@gmail.com", 'password' : "1q1w1e1r"})
