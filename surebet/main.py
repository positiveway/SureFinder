# from surebet.loading import *
# import surebet.loading.fonbet as fonbet_loading
# import surebet.loading.marat as marat_loading
#
# from surebet.parsing.bets import *
# import surebet.parsing.fonbet as fonbet_parsing
# import surebet.parsing.marat as marat_parsing
#
# from surebet.handling.searching import find_surebets
#
#
# selenium = Selenium()
#
# fonbet_loading.load(selenium.browser)
# fonbet_sample = fonbet_loading.load_events(selenium.browser)
#
# selenium.quit()
# # Marat
# marat_sample = marat_loading.load_events()
#
# bookmakers = Bookmakers()
# # parsing
# fonbet_parsing.parse(fonbet_sample, bookmakers.fonbet)
# marat_parsing.parse(marat_sample, bookmakers.marat)
#
# all_surebets = find_surebets(bookmakers)
#
# surebet_cnt = 0
# for books_surebets in all_surebets:
#     for sport_name in ("soccer", "basket", "hockey", "tennis", "volley"):
#         sport_surebets = getattr(books_surebets, sport_name)
#         for ev_surebets in sport_surebets:
#             print("{}\n{}".format(" vs ".join(ev_surebets.teams1), " vs ".join(ev_surebets.teams2)))
#             for part_surebets in ev_surebets.parts:
#                 surebets = part_surebets.surebets
#                 surebet_cnt += len(surebets)
# print(surebet_cnt)

from surebet.tests.test_integration import test_integration

test_integration()
