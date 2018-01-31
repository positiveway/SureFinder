import logging

from surebet.json_funcs import json_dumps
from surebet.loading import try_load
from surebet.loading.olimp import *
from surebet.tests.loading import check_result

min_size = 100


def test_loading():
    for i in range(7):
        print("load events: ({})".format(i))

        result = try_load(load_events, name)
        check_result(json_dumps(result), min_size)

    logging.info("PASS: loading")
