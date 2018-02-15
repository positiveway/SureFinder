import logging
import pickle
import json
from os import path

from surebet.tests.handling import package_dir
from surebet.json_funcs import json_dumps, obj_dumps
from surebet.handling.excluding import exclude_unpopular

resource_dir = path.join(package_dir, "unpopular")


def read_sample(filename):
    with open(path.join(resource_dir, filename), "rb") as found_file:
        obj = pickle.load(found_file)
    return obj


def test_sample():
    for sample_num in range(3):
        filename = 'sample{}.pkl'.format(sample_num)
        surebets = read_sample(filename)
        exclude_unpopular(surebets)

    logging.info("PASS: samples")


def test_known_result():
    surebets = read_sample("known.pkl")
    exclude_unpopular(surebets)

    with open(path.join(resource_dir, "knownResult.json")) as file_result:
        surebets_result = json.load(file_result)

    assert obj_dumps(surebets) == json_dumps(surebets_result)

    logging.info("PASS: known")
