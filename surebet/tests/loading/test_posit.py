import time
from requests import Session

from surebet.loading.posit import *
from surebet.loading.selenium import SeleniumService
from surebet.tests.loading import check_result
from surebet.bookmakers import Posit

from os import path
from unittest.mock import patch
import pickle
import logging


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


def test_load_events():
    with open(path.join(path.dirname(__file__), "posit", "sample.pkl"), "rb") as file_samples:
        samples = pickle.load(file_samples)
    iter_samples = iter(sorted(samples.keys()))

    def get_next_sample(load_func, site_name, **kwargs):  # it's called instead of try_load
        try:
            next_index = next(iter_samples)
        except StopIteration:
            raise AssertionError("Sample requests overflow") from StopIteration
        logging.info("PASS: requested sample {}".format(next_index))
        return samples[next_index]

    with patch('surebet.bookmakers.sleep') as mock_sleep:
        with patch('surebet.bookmakers.try_load') as mock_try_load:
            mock_try_load.side_effect = get_next_sample
            posit = Posit()
            posit.load_events()

    logging.info("PASS: load_events")
