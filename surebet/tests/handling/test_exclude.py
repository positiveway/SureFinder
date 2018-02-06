import logging
import pickle
import json
from os import path

from surebet.json_funcs import json_dumps, obj_dumps
from surebet.tests.handling import package_dir
from surebet.handling.excluding import exclude_posit

resource_dir = path.join(package_dir, "excluding")


def read_sample(filename):
    with open(path.join(resource_dir, filename), "rb") as found_file:
        obj = pickle.load(found_file)
    return obj[0], obj[1]


def surebets_to_json(surebets):
    for books in surebets.books_surebets:
        ad = books.attrs_dict()
        for sport in ad:
            for match in ad[sport]:
                match.teams1 = list(match.teams1)
                match.teams2 = list(match.teams2)
    return obj_dumps(surebets.books_surebets)


def test_known_result():
    surebets_other, surebets_posit = read_sample("known.pkl")
    exclude_posit(surebets_other, surebets_posit)

    with open(path.join(resource_dir, "known_result.json"), "r") as file_result:
        surebets_result = json.load(file_result)

    assert surebets_to_json(surebets_other) == json_dumps(surebets_result)

    logging.info("PASS: known")


def test_sample():
    for i in range(3):
        exclude_posit(*read_sample('sample{}.pkl'.format(i)))

    logging.info("PASS: samples")
