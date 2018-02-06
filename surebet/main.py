from surebet.bookmakers import Posit, Fonbet, Marat, Olimp
from surebet.handling.excluding import exclude_posit
from surebet.handling.searching import find_surebets
from surebet.loading.selenium import SeleniumService
from surebet.parsing.bets import Bookmakers


def start_scanning():
    posit = Posit()
    fonbet = Fonbet()
    marat = Marat()
    olimp = Olimp()

    bookmakers = Bookmakers()
    fonbet.load_events(bookmakers.fonbet)
    marat.load_events(bookmakers.marat)
    olimp.load_events(bookmakers.olimp)

    found_surebets = find_surebets(bookmakers)
    posit_surebets = posit.load_events()

    exclude_posit(found_surebets, posit_surebets)

    SeleniumService.quit()


if __name__ == "__main__":
    start_scanning()
