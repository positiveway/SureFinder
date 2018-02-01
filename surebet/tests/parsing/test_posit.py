import json
import logging

import pytest
from os import path

from surebet.json_funcs import obj_dumps, json_dumps
from surebet.parsing import ParseException
from surebet.parsing.posit import parse
from surebet.tests.parsing import package_dir, read_html

name = "posit"
resource_dir = path.join(package_dir, name)


def abs_path(filename):
    return path.join(resource_dir, filename)


def test_samples():
    for num in range(3):
        filename = abs_path('sample{}.html'.format(num))
        html = read_html(filename)

        parse(html)
        logging.info('PASS: sample{}'.format(num))


def test_known_result():
    filename = abs_path('knownRes.json')
    with open(filename) as file:
        known_res = json.load(file)

    filename = abs_path('knownRes.html')
    html = read_html(filename)

    surebets = parse(html)

    assert obj_dumps(surebets) == json_dumps(known_res)

    logging.info('PASS: known result')


def test_broken_structure():
    filename = abs_path('brokenStruct.html')
    html = read_html(filename)

    with pytest.raises(ParseException, message='Expecting ParseException'):
        parse(html)

    logging.info('PASS: broken structure')
