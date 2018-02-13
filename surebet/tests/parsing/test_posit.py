import json
import logging

import pytest
from os import path

from surebet.json_funcs import obj_dumps, json_dumps
from surebet.parsing import try_parse, ParseException
from surebet.parsing.posit import parse
from surebet.tests.parsing import abs_path, read_html, read_json

name = 'posit'


def test_samples():
    for num in range(3):
        filename = abs_path(name, 'sample{}.html'.format(num))
        html = read_html(filename)

        try_parse(parse, html, name)
        logging.info('PASS: sample{}'.format(num))


def test_known_result():
    filename = abs_path(name, 'knownResultIn.html')
    html = read_html(filename)

    filename = abs_path(name, 'knownResultOut.json')
    known_result = read_json(filename)

    surebets = try_parse(parse, html, name)

    assert obj_dumps(surebets) == json_dumps(known_result)

    logging.info('PASS: known result')


def test_broken_structure():
    filename = abs_path(name, 'brokenStructure.html')
    html = read_html(filename)

    with pytest.raises(ParseException, message='Expecting ParseException'):
        parse(html)

    logging.info('PASS: broken structure')

