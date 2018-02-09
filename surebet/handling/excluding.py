from surebet import find_in_iter, reverse_enum
from surebet.handling.surebets import Surebets, Surebet


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
