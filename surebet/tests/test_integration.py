from surebet import *

from surebet.loading import *
import surebet.loading.fonbet as fonbet_loading
import surebet.loading.marat as marat_loading

from surebet.parsing.bets import *
import surebet.parsing.fonbet as fonbet_parsing
import surebet.parsing.marat as marat_parsing

from surebet.handling.searching import find_surebets


def test_integration():
    # loading
    # Fonbet
    selenium = Selenium()

    fonbet_loading.load(selenium.browser)
    fonbet_sample = fonbet_loading.load_events(selenium.browser)

    selenium.quit()
    # Marat
    marat_sample = marat_loading.load_events()

    bookmakers = Bookmakers()
    # parsing
    fonbet_parsing.parse(fonbet_sample, bookmakers.fonbet)
    marat_parsing.parse(marat_sample, bookmakers.marat)

    find_surebets(bookmakers)

    logging.info("PASS: integration")
