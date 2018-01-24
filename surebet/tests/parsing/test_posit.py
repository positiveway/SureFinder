import pytest
from os import path

from surebet import *
from surebet.parsing import ParseException
from surebet.parsing.posit import parse
from surebet.tests.parsing import *
from surebet.handling import generate_all_surebets

name = "posit"
resource_dir = path.join(package_dir, name)


def abs_path(filename):
    return path.join(resource_dir, filename)


def test_samples():
    for num in range(3):
        filename = abs_path('sample{}.html'.format(num))
        with open(filename) as file:
            html = file.read()

        parse(html, generate_all_surebets())
        logging.info('PASS: sample{}'.format(num))


def test_known_result():
    filename = abs_path('knownRes.json')
    with open(filename) as file:
        known_res = json.load(file)

    filename = abs_path('knownRes.html')
    with open(filename) as file:
        html = file.read()

    all_surebets = generate_all_surebets()
    parse(html, all_surebets)

    assert obj_to_json(all_surebets) == json_dumps(known_res)

    logging.info('PASS: known result')


def test_broken_structure():
    filename = abs_path('brokenStruct.html')
    with open(filename) as file:
        html = file.read()

    with pytest.raises(ParseException, message='Expecting ParseException'):
        parse(html, generate_all_surebets())

    logging.info('PASS: broken structure')
