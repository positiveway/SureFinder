import time

from surebet import *
from surebet.loading import *
from surebet.loading.fonbet import load, load_events


def test_loading():
    selenium = Selenium()
    selenium.browser.implicitly_wait(30)

    for j in range(3):
        print("load: ({})".format(j))

        load(selenium.browser)
        for i in range(8):
            print("load events: ({})".format(i))

            result = load_events(selenium.browser)
            if len(result):
                print(len(result))
            else:
                raise LoadException("got empty html")

            time.sleep(2)

        time.sleep(5)

    selenium.quit()
    logging.info("PASS: loading")
