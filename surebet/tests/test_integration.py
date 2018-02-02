import logging

import surebet.loading.fonbet as fonbet_loading
import surebet.loading.marat as marat_loading
import surebet.loading.olimp as olimp_loading
import surebet.parsing.fonbet as fonbet_parsing
import surebet.parsing.marat as marat_parsing
import surebet.parsing.olimp as olimp_parsing
from surebet.bookmakers import Posit
from surebet.handling.excluding import exclude_posit
from surebet.handling.searching import find_surebets
from surebet.loading.selenium import SeleniumService
from surebet.parsing.bets import Bookmakers


def test_integration():
    # loading
    sel_service = SeleniumService()

    posit = Posit()

    fonbet_sel = sel_service.new_instance()

    fonbet_loading.load(fonbet_sel.browser)
    fonbet_sample = fonbet_loading.load_events(fonbet_sel.browser)

    marat_sample = marat_loading.load_events()

    olimp_sample = olimp_loading.load_events()

    bookmakers = Bookmakers()
    # parsing
    fonbet_parsing.parse(fonbet_sample, bookmakers.fonbet)
    marat_parsing.parse(marat_sample, bookmakers.marat)
    olimp_parsing.parse(olimp_sample, bookmakers.olimp)

    found_surebets = find_surebets(bookmakers)
    posit_surebets = posit.load_events()

    exclude_posit(found_surebets, posit_surebets)

    sel_service.quit()

    logging.info("PASS: integration")
