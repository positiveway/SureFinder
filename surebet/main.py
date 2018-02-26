from threading import Thread, Lock

from surebet.bookmakers import Posit, Fonbet, Marat, Olimp
from surebet.handling.detailed_surebets import convert_to_detailed
from surebet.handling.excluding import exclude_posit, exclude_unpopular
from surebet.handling.searching import find_surebets
from surebet.handling.surebets import Surebets
from surebet.loading.selenium import SeleniumService
from surebet.parsing.bets import Bookmakers


class SafeSurebets:
    """Thread safe class to store detailed_surebets"""

    def __init__(self):
        self._detailed_surebets = None
        self.lock = Lock()

    @property
    def detailed_surebets(self):
        with self.lock:
            return self._detailed_surebets

    @detailed_surebets.setter
    def detailed_surebets(self, detailed_surebets):
        with self.lock:
            self._detailed_surebets = detailed_surebets


def start_scanning(iter_num=None):
    posit = Posit()
    fonbet = Fonbet()
    marat = Marat()
    olimp = Olimp()

    old_surebets = Surebets()

    def make_iteration():
        nonlocal old_surebets

        bookmakers = Bookmakers()
        fonbet.load_events(bookmakers.fonbet)
        marat.load_events(bookmakers.marat)
        olimp.load_events(bookmakers.olimp)

        posit_surebets = posit.load_events()
        surebets = find_surebets(bookmakers)

        exclude_posit(surebets, posit_surebets)

        exclude_unpopular(surebets)

        surebets.set_timestamps(old_surebets)
        old_surebets = surebets

        return convert_to_detailed(surebets)

    if iter_num is None:
        while True:
            yield make_iteration()
    else:
        for i in range(iter_num):
            yield make_iteration()

    SeleniumService.quit()


def main(iter_num=None):
    from surebet.ui.server import run_server

    safe_surebets = SafeSurebets()

    server = Thread(target=run_server, args=(safe_surebets,))
    server.start()

    print("Scanner is started")

    for idx, detailed_surebets in enumerate(start_scanning(iter_num)):
        safe_surebets.detailed_surebets = detailed_surebets

        print("ITERATION #{}".format(idx))

        for detailed_surebet in detailed_surebets:
            print(detailed_surebet)

        print()

    server.join()


if __name__ == "__main__":
    main(10)
