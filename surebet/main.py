from surebet.loading import *
from surebet.loading.fonbet import save

selenium = Selenium()
save(selenium.browser)
selenium.quit()
