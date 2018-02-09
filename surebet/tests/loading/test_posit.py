import time
import json

from unittest.mock import patch
from requests import Session

from surebet.tests import SurebetsJSONDecoder
from surebet.json_funcs import json_dumps, obj_dumps, obj_dump
from surebet.loading.posit import *
from surebet.tests.loading import check_result, package_dir
from surebet.bookmakers import Posit

import logging
from os import path

resource_dir = path.join(package_dir, 'posit')


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


def mock_load_events(sample):
    iter_sample = iter(sample)

    def get_next_html(load_func, site_name, **kwargs):  # it's called instead of try_load
        try:
            sample_next = next(iter_sample)
        except StopIteration:
            raise AssertionError("Sample requests overflow") from StopIteration

        return sample_next

    with patch("surebet.bookmakers.sleep") as mock_sleep:
        with patch("surebet.bookmakers.try_load") as mock_try_load:
            mock_try_load.side_effect = get_next_html
            posit = Posit()
            surebets_posit = posit.load_events()

    return surebets_posit


def test_sample():
    for sample_num in range(3):
        filename = path.join(resource_dir, "sample{}.json".format(sample_num))
        with open(filename) as file_sample:
            sample = json.load(file_sample)

        mock_load_events(sample)

    logging.info("PASS: samples")


def test_known_result():
    with open(path.join(resource_dir, "known.json")) as file_known:
        sample_known = json.load(file_known)
    surebets_posit = mock_load_events(sample_known)

    with open(path.join(resource_dir, "knownResult.json")) as file_known_result:
        surebets_known = json.load(file_known_result)

    assert obj_dumps(surebets_posit) == json_dumps(surebets_known)

    logging.info("PASS: known result")


@patch('surebet.bookmakers.sleep')
def mock_posit(mock_sleep):
    with patch("surebet.bookmakers.try_load") as mock_try_load:
        mock_try_load.return_value = ""  # needed for first try_load call in Posit's constructor
        with patch('surebet.bookmakers.Posit._add_new_surebets') as mock_add_new:
            mock_add_new.return_value = 0
            result = Posit()

    return result


@patch('surebet.bookmakers.sleep')
def mock_decrease_marks(posit, mock_sleep):
    filename = path.join(resource_dir, 'knownDecreaseLoads.json')
    with open(filename) as file_loads:
        list_loads = json.load(file_loads)

    iter_loads = iter(list_loads)

    def load_next_html(load_func, site_name, **kwargs):  # it's called instead of try_load
        return next(iter_loads)

    with patch("surebet.bookmakers.try_load") as mock_try_load:
        mock_try_load.side_effect = load_next_html
        for load_idx in range(len(list_loads)):
            print('загрузка номер {}'.format(load_idx))
            posit.load_events()


def test_decrease_known():
    with open(path.join(resource_dir, 'knownDecrease.json')) as file_known:
        surebets = json.load(file_known, cls=SurebetsJSONDecoder)

    posit = mock_posit()
    posit.surebets = surebets
    mock_decrease_marks(posit)

    with open(path.join(resource_dir, 'knownDecreaseResult.json')) as file_known_result:
        surebets_known = json.load(file_known_result)

    assert obj_dumps(posit.surebets) == json_dumps(surebets_known)
