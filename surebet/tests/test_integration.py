import logging

import surebet.loading.fonbet as fonbet_loading
import surebet.loading.marat as marat_loading
import surebet.parsing.fonbet as fonbet_parsing
import surebet.parsing.marat as marat_parsing
from surebet.bookmakers import Posit
from surebet.handling.excluding import exclude_posit
from surebet.handling.searching import find_surebets
from surebet.loading.selenium import Selenium
from surebet.parsing.bets import Bookmakers


def test_integration():
    # loading
    posit = Posit()

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

    found_surebets = find_surebets(bookmakers)
    posit_surebets = posit.load_events()
    exclude_posit(found_surebets, posit_surebets)

    posit.quit()

    logging.info("PASS: integration")
