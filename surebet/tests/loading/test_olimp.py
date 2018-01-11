from surebet import *
from surebet.loading import LoadException
from surebet.loading.olimp import load_events


def test_loading():
    for i in range(7):
        print("iteration: ({})".format(i))

        result = load_events()

        result_size = len(result)
        if result_size:
            print(result_size)
        else:
            raise LoadException("got empty html")

    logging.info("PASS: loading")


