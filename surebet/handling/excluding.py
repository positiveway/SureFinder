from re import search

from surebet import find_in_iter, reverse_enum
from surebet.handling.surebets import Surebets, Surebet

women_patterns = ["\(W\)", "\(w\)"]
other_patterns = ["\(R\)", "\(r\)", "U\d+", "\(U\d+\)", "U-\d+", "Reserves"]


def _del_equal(found_obj, posit_obj) -> None:
    for attr, found_iter in found_obj.__dict__.items():
        if isinstance(found_iter, list):
            posit_iter = getattr(posit_obj, attr)
            for idx, found_el in reverse_enum(found_iter):
                posit_el = find_in_iter(posit_iter, found_el)
                if posit_el:
                    if isinstance(found_el, Surebet):
                        del found_iter[idx]
                    # object can contain lists that should not be handled by algorithm
                    # e.g. teams is list of strings, srt is primitive type without __dict__ method
                    elif hasattr(found_el, '__dict__'):
                        _del_equal(found_el, posit_el)


def exclude_posit(found_surebets: Surebets, posit_surebets: Surebets) -> None:
    _del_equal(found_surebets, posit_surebets)
    found_surebets.format()


def exclude_unpopular(surebets):
    for book in surebets.books_surebets:
        for sport_name, sport in book.attrs_dict().items():
            patterns = list(other_patterns)
            if sport_name != "volley":  # volleyball women teams are allowed
                patterns += women_patterns

            for idx, event in reverse_enum(sport):
                if is_unpopular(patterns, event):
                    del sport[idx]


def is_unpopular(patterns, event):
    for pattern in patterns:
        for teams in (event.teams1, event.teams2):
            if search(pattern, teams[0]) or search(pattern, teams[1]):
                return True
    return False
