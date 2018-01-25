from surebet import *
from surebet.loading import try_load
from surebet.loading.olimp import load_events, name
from surebet.tests.loading import *

min_size = 100


def test_loading():
    for i in range(7):
        print("load events: ({})".format(i))

        result = try_load(load_events, name)
        check_result(json_dumps(result), min_size)

    logging.info("PASS: loading")
