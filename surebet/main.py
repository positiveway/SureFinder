# from surebet.handling.searching import find_surebets
# from surebet.loading.selenium import Selenium
# from surebet.parsing.bets import *
#
# posit_sel, fonbet_sel = None, None
#
#
# def load_all():
#     from surebet.loading import fonbet, posit
#
#     global posit_sel, fonbet_sel
#
#     posit_sel = Selenium()
#     posit.load(posit_sel.browser)
#
#     fonbet_sel = Selenium()
#     fonbet.load(fonbet_sel.browser)
#
#
# def load_all_events():
#     from surebet.loading import fonbet, marat, posit
#
#     posit_events = posit.load_events(posit_sel.browser)
#     fonbet_events = fonbet.load_events(fonbet_sel.browser)
#
#     marat_events = marat.load_events()
#
#
# def cleanup():
#     posit_sel.quit()
#     fonbet_sel.quit()
#
#
# def parse_all(bookmakers, posit_surebets):
#     from surebet.parsing import fonbet, marat, posit
#
#     fonbet.parse(fonbet_events, bookmakers.fonbet)
#     marat.parse(marat_events, bookmakers.marat)
#
#     posit.parse(posit_events, posit_surebets)
#
#
# def handle_all():
#     load_all()
#
#     posit_surebets = []
#
#     for i in range(10):
#         load_all_events()
#
#         bookmakers = Bookmakers()
#         parse_all(bookmakers, posit_surebets)
#
#         found_surebets = find_surebets(bookmakers)
#
#     cleanup()
from surebet.tests.test_integration import test_integration

test_integration()
