from surebet import *
from surebet.loading import try_load
from surebet.loading.olimp import load, load_events, name
from surebet.tests.loading import *

min_size = 100


def test_loading():
    for j in range(2):
        print("load: ({})".format(j))

        try_load(load, name)
        for i in range(5):
            print("load events: ({})".format(i))

            result = try_load(load_events, name)
            check_result(json_dumps(result), min_size)

    logging.info("PASS: loading")
