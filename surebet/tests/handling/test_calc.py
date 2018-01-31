import json
import logging
import pickle

from os import path

from surebet.handling.calculating import calc_surebets
from surebet.json_funcs import obj_dumps, json_dumps
from surebet.tests.handling import package_dir

resource_dir = path.join(package_dir, "calculating")


def test_known_result():
    filename = path.join(resource_dir, "knownResult.json")
    with open(filename) as file:
        known_res = json.load(file)

    filename = path.join(resource_dir, "knownResult.pkl")
    with open(filename, "rb") as file:
        known_res_sample = pickle.load(file)

    surebets = calc_surebets(*known_res_sample)

    assert obj_dumps(surebets) == json_dumps(known_res)

    logging.info("PASS: known result")


def test_sample():
    filename = path.join(resource_dir, "sample.pkl")
    with open(filename, "rb") as file:
        sample = pickle.load(file)

    sample[0].sort(key=lambda o: o["sport"])
    sample[1].sort(key=lambda o: o["sport"])
    for bets_pair in range(len(sample[0])):
        part1, part2 = sample[0][bets_pair], sample[1][bets_pair]
        wagers_bets = (part1["part_bets"], part2["part_bets"])
        if part1["sport"] == "tennis" or part1["sport"] == "volley":
            calc_surebets(*wagers_bets, with_draw=False)
        else:
            calc_surebets(*wagers_bets)

    logging.info("PASS: sample")
