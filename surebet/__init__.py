import json
import logging

import os

package_dir = os.path.dirname(__file__)

# setup default logging level
logging.basicConfig(level=logging.INFO)

_json_params = {'indent': '\t', 'sort_keys': True}
_convert_func = {'default': lambda o: o.__dict__}


def json_dump(obj, fp, **kwargs):
    json.dump(obj, fp, **_json_params, **kwargs)


def json_dumps(obj, **kwargs):
    return json.dumps(obj, **_json_params, **kwargs)


def obj_dump(obj, fp):
    return json_dump(obj, fp, **_convert_func)


def obj_dumps(obj):
    return json_dumps(obj, **_convert_func)


def find_by_predicate(iterable, predicate):
    # return first occurrence or None
    return next((el for el in iterable if predicate(el)), None)


def find_in_iter(iterable, el):
    try:
        # return value from iterable equal to el
        return iterable[iterable.index(el)]
    except ValueError:
        return None
