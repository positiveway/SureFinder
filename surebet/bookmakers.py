from time import sleep

from surebet import find_in_iter
from surebet.handling.surebets import *
from surebet.loading.posit import *
from surebet.loading.selenium import Selenium
from surebet.parsing.posit import parse


class Posit:
    def __init__(self, account=default_account):
        self.selenium = Selenium()
        try_load(load, name, browser=self.selenium.browser, account=account)

        self.surebets = Surebets()

        new_added = None
        while new_added != 0:
            new_added = self._add_new_surebets()

            sleep(6)  # wait for positive to auto refresh page

    def _add_new_surebets(self):
        sample = try_load(load_events, name, browser=self.selenium.browser)
        new_surebets = parse(sample)

        self._decrease_marks()
        new_added = self._merge_surebets(new_surebets)
        # self.surebets.format()  # TODO: need to implement method format

        return new_added

    def _decrease_marks(self):
        for book in self.surebets.books_surebets:
            for sport in book.attrs_dict().values():
                for event in sport:
                    for part in event.parts:
                        for surebet in part.surebets:
                            surebet.dec_mark()

                            if not surebet.mark:
                                part.surebets.remove(surebet)

    def _merge_surebets(self, new_surebets):
        new_added = 0

        for new_book in new_surebets.books_surebets:
            book = find_in_iter(self.surebets.books_surebets, new_book)

            for sport_name, new_sport in new_book.attrs_dict().items():
                sport = getattr(book, sport_name)

                for new_event in new_sport:
                    event = find_in_iter(sport, new_event)
                    if not event:
                        event = EventSurebets(new_event.teams1, new_event.teams2)
                        sport.append(event)

                    for new_part in new_event.parts:
                        part = find_in_iter(event.parts, new_part)
                        if not part:
                            part = PartSurebets([], new_part.part)
                            event.parts.append(part)

                        for new_surebet in new_part.surebets:
                            surebet = find_in_iter(part.surebets, new_surebet)
                            if surebet:
                                surebet.restore_mark()
                            else:
                                part.surebets.append(new_surebet)
                                new_added += 1

        return new_added

    def load_events(self):
        self._add_new_surebets()
        return self.surebets

    def cleanup(self):
        self.selenium.quit()
