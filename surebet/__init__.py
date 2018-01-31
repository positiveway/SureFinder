import logging

import os

package_dir = os.path.dirname(__file__)

# setup default logging level
logging.basicConfig(level=logging.INFO)


def find_by_predicate(iterable, predicate):
    # return first occurrence or None
    return next((el for el in iterable if predicate(el)), None)


def find_in_iter(iterable, el):
    try:
        # return value from iterable equal to el
        return iterable[iterable.index(el)]
    except ValueError:
        return None
