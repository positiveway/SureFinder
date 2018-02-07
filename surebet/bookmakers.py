from time import sleep
from requests import Session

from surebet import find_in_iter
from surebet.handling.surebets import *
from surebet.loading import try_load
from surebet.parsing import try_parse
from surebet.loading.posit import default_account
from surebet.loading.selenium import SeleniumService

LOAD_INTERVAL = 6

INIT_ITER = 7
THRESHOLD_INIT = 3

INC_EVERY = 3
THRESHOLD_INC = 2


class Posit:
    def __init__(self, account=default_account):
        from surebet.loading.posit import load, name

        self.session = Session()
        try_load(load, name, session=self.session, account=account)

        self.surebets = Surebets()

        threshold = 0
        last_inc_iter = 0
        cur_iter = 0
        while self._add_new_surebets() > threshold:
            if cur_iter == INIT_ITER:
                threshold = THRESHOLD_INIT
                last_inc_iter = cur_iter
            elif cur_iter > INIT_ITER and cur_iter - last_inc_iter == INC_EVERY:
                # Increasing the threshold
                threshold += THRESHOLD_INC
                last_inc_iter = cur_iter

            cur_iter += 1
            sleep(LOAD_INTERVAL)  # wait for positive to auto refresh page

    def _add_new_surebets(self) -> int:  # returns amount of newly added surebets
        from surebet.loading.posit import load_events, name
        from surebet.parsing.posit import parse

        sample = try_load(load_events, name, session=self.session)
        new_surebets = try_parse(parse, sample, name)

        self._decrease_marks()
        new_added = self._merge_surebets(new_surebets)
        self.surebets.format()

        return new_added

    def _decrease_marks(self):
        for book in self.surebets.books_surebets:
            for sport in book.attrs_dict().values():
                for event in sport:
                    for part in event.parts:
                        for surebet in part.surebets:
                            surebet.dec_mark()

                            if surebet.is_mark_empty():
                                part.surebets.remove(surebet)

    def _merge_surebets(self, new_surebets) -> int:  # returns amount of newly added surebets
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


class Fonbet:
    def __init__(self):
        from surebet.loading.fonbet import load, name

        self.selenium = SeleniumService().new_instance()
        try_load(load, name, browser=self.selenium.browser)

    def load_events(self, bookmaker):
        from surebet.loading.fonbet import load_events, name
        from surebet.parsing.fonbet import parse

        sample = try_load(load_events, name, browser=self.selenium.browser)
        try_parse(parse, sample, name, bookmaker=bookmaker)


class Marat:
    def load_events(self, bookmaker):
        from surebet.loading.marat import load_events, name
        from surebet.parsing.marat import parse

        sample = try_load(load_events, name)
        try_parse(parse, sample, name, bookmaker=bookmaker)


class Olimp:
    def load_events(self, bookmaker):
        from surebet.loading.olimp import load_events, name
        from surebet.parsing.olimp import parse

        sample = try_load(load_events, name)
        try_parse(parse, sample, name, bookmaker=bookmaker)
