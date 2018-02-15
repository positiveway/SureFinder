from surebet.bookmakers import Posit, Fonbet, Marat, Olimp
from surebet.handling.detailed_surebets import convert_to_detailed
from surebet.handling.excluding import exclude_posit
from surebet.handling.searching import find_surebets
from surebet.handling.surebets import Surebets
from surebet.loading.selenium import SeleniumService
from surebet.parsing.bets import Bookmakers


def start_scanning(iter_num):
    print("Scanner is started")

    posit = Posit()
    fonbet = Fonbet()
    marat = Marat()
    olimp = Olimp()

    old_surebets = Surebets()
    for i in range(iter_num):
        print("ITERATION #{}".format(i))

        bookmakers = Bookmakers()
        fonbet.load_events(bookmakers.fonbet)
        marat.load_events(bookmakers.marat)
        olimp.load_events(bookmakers.olimp)

        posit_surebets = posit.load_events()
        surebets = find_surebets(bookmakers)

        exclude_posit(surebets, posit_surebets)

        surebets.set_timestamps(old_surebets)
        old_surebets = surebets

        detailed_surebets = convert_to_detailed(surebets)
        for detailed_surebet in detailed_surebets:
            print(detailed_surebet)

        print()

    SeleniumService.quit()


if __name__ == "__main__":
    start_scanning(10)
