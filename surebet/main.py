from surebet.loading import *
from surebet.loading.fonbet import load

selenium = Selenium()
load(selenium.browser)
selenium.quit()
