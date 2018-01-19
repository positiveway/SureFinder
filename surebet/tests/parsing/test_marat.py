import pytest
from os import path

from surebet import *
from surebet.parsing import ParseException
from surebet.parsing.bets import Bookmaker
from surebet.parsing.marat import parse
from surebet.tests.parsing import *

name = "marat"
resource_dir = path.join(package_dir, name)


def abs_path(filename):
    return path.join(resource_dir, filename)


def test_samples():
    for num in range(3):
        filename = abs_path('sample{}.json'.format(num))
        with open(filename) as file:
            sample = json.load(file)
        parse(sample, Bookmaker(name))
        logging.info('PASS: sample{}'.format(num))


def test_known_result():
    known_result_out_file = abs_path("knownResultOut.json")
    with open(known_result_out_file) as file:
        known_result = json.load(file)

    known_result_in_file = abs_path("knownResultIn.json")
    with open(known_result_in_file) as file:
        known_result_in = json.load(file)

    marat = Bookmaker(name)
    parse(known_result_in, marat)
    marat.format()

    assert obj_to_json(marat) == json_dumps(known_result)

    logging.info('PASS: known result')


def test_broken_structure():
    filename = abs_path('brokenStructure.json')
    with open(filename) as file:
        broken_sample = json.load(file)

    with pytest.raises(ParseException, message='Expecting ParseException'):
        parse(broken_sample, Bookmaker(name))

    logging.info('PASS: broken structure')
