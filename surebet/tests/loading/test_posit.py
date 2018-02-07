import time
from requests import Session

from surebet.loading.posit import *
from surebet.tests.loading import check_result


def test_loading():
    session = Session()

    print("loaded")

    try_load(load, name, session=session)
    for i in range(4):
        print("load events: ({})".format(i))

        result = try_load(load_events, name, session=session)
        check_result(result)

        time.sleep(1)

    logging.info("PASS: loading")
