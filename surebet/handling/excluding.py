from surebet import find_in_iter
from surebet.handling.surebets import Surebets, Surebet


def _del_equal(found_obj, posit_obj) -> None:
    for attr, found_iter in found_obj.__dict__.items():
        if isinstance(found_iter, list):
            posit_iter = getattr(posit_obj, attr)
            for found_el in list(found_iter):
                posit_el = find_in_iter(posit_iter, found_el)
                if posit_el:
                    if isinstance(found_el, Surebet):
                        found_iter.remove(found_el)
                    else:
                        exclude_from_posit(found_el, posit_el)


def exclude_from_posit(found_surebets: Surebets, posit_surebets: Surebets) -> None:
    _del_equal(found_surebets, posit_surebets)
