from surebet.loading.fonbet import load
from surebet.loading.selenium import Selenium

selenium = Selenium()
load(selenium.browser)
selenium.quit()
