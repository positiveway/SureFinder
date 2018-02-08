import time
import pickle
import json

from unittest.mock import patch
from requests import Session

from surebet.json_funcs import json_dumps, obj_dumps
from surebet.loading.posit import *
from surebet.loading.selenium import SeleniumService
from surebet.tests.loading import check_result
from surebet.bookmakers import Posit

import logging
from os import path


resource_dir = path.join(path.dirname(__file__), "posit")


def test_loading():
    session = Session()

    print("loaded")

    try_load(load, name, session=session)
    for i in range(4):
        print("load events: ({})".format(i))

        result = try_load(load_events, name, session=session)
        check_result(result)

        time.sleep(1)

    SeleniumService.quit()

    logging.info("PASS: loading")


def mock_load_events(sample):
    iter_samples = iter(sorted(sample.keys()))

    def get_next_html(load_func, site_name, **kwargs):  # it's called instead of try_load
        try:
            next_index = next(iter_samples)
        except StopIteration:
            raise AssertionError("Sample requests overflow") from StopIteration

        return sample[next_index]

    with patch("surebet.bookmakers.sleep") as mock_sleep:
        with patch("surebet.bookmakers.try_load") as mock_try_load:
            mock_try_load.side_effect = get_next_html
            posit = Posit()
            surebets_posit = posit.load_events()

    return surebets_posit


def test_sample():
    for i in range(1):
        with open(path.join(resource_dir, "sample{}.pkl".format(i)), "rb") as file_sample:
            sample = pickle.load(file_sample)
        mock_load_events(sample)

    logging.info("PASS: samples")


def test_known_result():
    with open(path.join(resource_dir, "known.pkl"), "rb") as file_known:
        sample_known = pickle.load(file_known)
    surebets_posit = mock_load_events(sample_known)

    with open(path.join(resource_dir, "knownResult.json")) as file_known_result:
        surebets_known = json.load(file_known_result)

    assert obj_dumps(surebets_posit) == json_dumps(surebets_known)

    logging.info("PASS: known result")
