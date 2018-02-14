import json
import logging

import pytest
from os import path
from importlib import import_module

from surebet.json_funcs import obj_dumps, json_dumps
from surebet.parsing import try_parse, ParseException
from surebet.parsing.bets import Bookmaker

package_dir = path.dirname(__file__)


def abs_path(name, filename):
    return path.join(package_dir, name, filename)


def file_extension(filename):
    return path.splitext(filename)[-1][1:]


def read_html(filename) -> str:
    with open(filename, encoding='utf8') as file:
        return file.read()


def read_json(filename):
    with open(filename) as file:
        return json.load(file)


def read_sample(name, filename):
    filename = abs_path(name, filename)
    if file_extension(filename) == 'html':
        return read_html(filename)
    return read_json(filename)


def test_samples(name, samplefile_extension):
    parse = import_module('surebet.parsing.' + name).parse
    for num in range(3):
        sample = read_sample(name, 'sample{}.{}'.format(num, samplefile_extension))
        try_parse(parse, sample, name, bookmaker=Bookmaker(name))
        logging.info('PASS: sample{}'.format(num))


def test_broken_structure(name, broken_structure_file_extension):
    parse = import_module('surebet.parsing.' + name).parse
    broken_sample = read_sample(name, 'brokenStructure.' + broken_structure_file_extension)
    with pytest.raises(ParseException, message='Expecting ParseException'):
        parse(broken_sample, Bookmaker(name))
    logging.info('PASS: broken structure')


def test_known_result(name, known_result_in_file_extension):
    parse = import_module('surebet.parsing.' + name).parse

    known_result_in = read_sample(name, 'knownResultIn.' + known_result_in_file_extension)
    known_result_out = read_sample(name, 'knownResultOut.json')

    bookmaker = Bookmaker(name)
    try_parse(parse, known_result_in, name, bookmaker=bookmaker)
    bookmaker.format()

    assert obj_dumps(bookmaker) == json_dumps(known_result_out)

    logging.info('PASS: known result')


def test_bookmaker(name, extension):
    test_samples(name, extension)
    test_broken_structure(name, extension)
    test_known_result(name, extension)
