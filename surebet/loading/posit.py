from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def log_in(browser, account):
    browser.get("http://positivebet.com/en")
    browser.find_element_by_link_text("Login").send_keys(Keys.RETURN)
    browser.find_element_by_id("UserLogin_username").send_keys(account['login'])
    browser.find_element_by_id("UserLogin_password").send_keys(account['password'])
    browser.find_element_by_name("yt0").send_keys(Keys.RETURN)
    # after logging into account we're redirecting on the main page and then...
    # seems like the button "Home" (on the site) is pressing by site right after main page was loaded,
    # so if we will try to click on "Live bets" button right after main page is loaded, we will do this, ok,
    # but right after this site clicks on "Home" button and we stay on main page
    # that's why next command is used 2 times (or may be we should just wait for something?)
    browser.find_element_by_link_text("Live bets").send_keys(Keys.RETURN)
    browser.find_element_by_link_text("Live bets").send_keys(Keys.RETURN)
    browser.find_element_by_name("yt1").send_keys(Keys.RETURN)
    # in the process...
    browser.close()


log_in(webdriver.Chrome(), {'login' : "kolyan312@gmail.com", 'password' : "1q1w1e1r"})
