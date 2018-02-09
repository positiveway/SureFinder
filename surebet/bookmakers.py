from time import sleep
from requests import Session

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

FORBIDDEN_INTERVAL = 30 * 60  # time in seconds

MAX_ERR_CNT = 5


class Posit:
    def __init__(self, account=default_account):
        self.err_handler = ErrorHandler()

        self.session = Session()
        self.account = account
        self.load()

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

    def load(self):
        from surebet.loading.posit import load, name

        @self.err_handler.handle_error
        def _load():
            try_load(load, name, session=self.session, account=self.account)

        return _load()

    def _add_new_surebets(self) -> int:  # returns amount of newly added surebets
        new_surebets = self.get_new_surebets()

        self._decrease_marks()
        new_added = self._merge_surebets(new_surebets)
        self.surebets.format()

        return new_added

    def get_new_surebets(self):
        from surebet.loading.posit import load_events, name
        from surebet.parsing.posit import parse

        @self.err_handler.handle_error
        def _get_new_surebets():
            sample = try_load(load_events, name, session=self.session)
            return try_parse(parse, sample, name)

        return _get_new_surebets()

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

        if new_surebets is None:
            return new_added

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
        self.err_handler = ErrorHandler()

        self.selenium = SeleniumService().new_instance()
        self.load()

    def load(self):
        from surebet.loading.fonbet import load, name

        @self.err_handler.handle_error
        def _load():
            try_load(load, name, browser=self.selenium.browser)

        return _load()

    def load_events(self, bookmaker):
        from surebet.loading.fonbet import load_events, name
        from surebet.parsing.fonbet import parse

        @self.err_handler.handle_error
        def _load_events():
            sample = try_load(load_events, name, browser=self.selenium.browser)
            try_parse(parse, sample, name, bookmaker=bookmaker)

        return _load_events()


class Marat:
    def __init__(self):
        self.err_handler = ErrorHandler()

    def load_events(self, bookmaker):
        from surebet.loading.marat import load_events, name
        from surebet.parsing.marat import parse

        @self.err_handler.handle_error
        def _load_events():
            sample = try_load(load_events, name)
            try_parse(parse, sample, name, bookmaker=bookmaker)

        return _load_events()


class Olimp:
    def __init__(self):
        self.err_handler = ErrorHandler()

    def load_events(self, bookmaker):
        from surebet.loading.olimp import load_events, name
        from surebet.parsing.olimp import parse

        @self.err_handler.handle_error
        def _load_events():
            sample = try_load(load_events, name)
            try_parse(parse, sample, name, bookmaker=bookmaker)

        return _load_events()


class ErrorHandler:
    def __init__(self):
        self.error_cnt = 0
        self.first_occurred = 0

    def handle_error(self, func):
        def wrapper():
            try:
                return func()
            except Exception as err:
                # if it wasn't a forced stop of a program
                if not isinstance(err, KeyboardInterrupt):
                    # if first error and current error occurred within forbidden interval
                    if default_timer() - self.first_occurred < FORBIDDEN_INTERVAL:
                        if self.error_cnt >= MAX_ERR_CNT:
                            raise
                        else:
                            self.error_cnt += 1
                    else:
                        # refresh counter and measure time of first occurrence
                        self.error_cnt = 1
                        self.first_occurred = default_timer()
                else:
                    raise

            return None

        return wrapper
