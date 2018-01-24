from surebet import *
from surebet.loading import LoadException
from surebet.loading.olimp import load, load_events


min_size = 100


def test_loading():
    for j in range(2):
        print("load: ({})".format(j))

        load()
        for i in range(5):
            print("load events: ({})".format(i))

            result = load_events()

            result_size = len(json_dumps(result))
            if result_size < min_size:
                raise LoadException("result with small size")
            else:
                print(result_size)

    logging.info("PASS: loading")


