import json
import logging

import pytest
from os import path

from surebet.json_funcs import obj_dumps, json_dumps
from surebet.parsing import try_parse, ParseException
from surebet.parsing.bets import Bookmaker
from surebet.parsing.olimp import parse
from surebet.tests.parsing import package_dir

name = 'olimp'
resource_dir = path.join(package_dir, name)


def abs_path(filename):
    return path.join(resource_dir, filename)


def test_samples():
    for num in range(3):
        filename = abs_path('sample{}.json'.format(num))
        with open(filename) as file:
            sample = json.load(file)
        try_parse(parse, sample, name, bookmaker=Bookmaker(name))
        logging.info('PASS: sample{}'.format(num))


def test_known_result():
    with open(abs_path("knownResultIn.json")) as file:
        raw_data = json.load(file)

    with open(abs_path("knownResultOut.json")) as file:
        handled_data = json.load(file)

    olimp = Bookmaker(name)
    try_parse(parse, raw_data, name, bookmaker=olimp)
    olimp.format()

    assert obj_dumps(olimp) == json_dumps(handled_data)

    logging.info('PASS: known result')


def test_broken_structure():
    filename = abs_path('brokenStructure.json')
    with open(filename) as file:
        broken_sample = json.load(file)

    with pytest.raises(ParseException, message='Expecting ParseException'):
        parse(broken_sample, Bookmaker(name))

    logging.info('PASS: broken structure')
