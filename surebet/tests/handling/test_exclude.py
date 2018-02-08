import logging
import pickle
import json
from os import path

from surebet.json_funcs import json_dumps, obj_dumps
from surebet.handling.excluding import exclude_posit

resource_dir = path.join(path.dirname(__file__), "excluding")


def read_sample(filename):
    with open(path.join(resource_dir, filename), "rb") as found_file:
        obj = pickle.load(found_file)
    return obj[0], obj[1]


def test_sample():
    for i in range(3):
        exclude_posit(*read_sample('sample{}.pkl'.format(i)))

    logging.info("PASS: samples")


def test_known_result():
    surebets_other, surebets_posit = read_sample("known.pkl")
    exclude_posit(surebets_other, surebets_posit)

    with open(path.join(resource_dir, "knownResult.json"), "r") as file_result:
        surebets_result = json.load(file_result)

    assert obj_dumps(surebets_other) == json_dumps(surebets_result)

    logging.info("PASS: known")
