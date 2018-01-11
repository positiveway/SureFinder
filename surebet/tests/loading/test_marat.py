from json import dumps

from surebet import *
from surebet.loading import LoadException
from surebet.loading.marat import load_events


allowable_ratio = 0.85
min_size = 100


def test_loading():
    for i in range(7):
        print("iteration: ({})".format(i))

        result = load_events()

        result_size = len(dumps(result))
        if result_size < min_size:
            raise LoadException("result with small size")
        else:
            print(result_size)

        events_amount = get_events_amount(result["sport_tree"])
        if len(result["events"]) < int(events_amount * allowable_ratio):
            raise LoadException("got too few events")

    logging.info("PASS: loading")


def get_events_amount(sport_tree):
    amount = 0
    for sport in sport_tree:
        amount += len(sport["events"])
    return amount
