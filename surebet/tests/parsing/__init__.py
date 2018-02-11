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
    return path.splitext(filename)[1]


def read_sample(name, filename):
    filename = abs_path(name, filename)
    if file_extension(filename) == '.html':
        with open(filename, encoding='utf8') as file:
            return file.read()
    with open(filename) as file:
        return json.load(file)


def test_samples(name, samplefile_extension):
    parse = import_module('surebet.parsing.' + name).parse
    for num in range(3):
        sample = read_sample(name, 'sample{}.{}'.format(num, samplefile_extension))
        if name == 'posit':
            try_parse(parse, sample, name)
        else:
            try_parse(parse, sample, name, bookmaker=Bookmaker(name))
        logging.info('PASS: sample{}'.format(num))


def test_broken_structure(name, filename):
    parse = import_module('surebet.parsing.' + name).parse
    broken_sample = read_sample(name, filename)
    with pytest.raises(ParseException, message='Expecting ParseException'):
        if name == 'posit':
            parse(broken_sample)
        else:  # bookmaker
            parse(broken_sample, Bookmaker(name))
    logging.info('PASS: broken structure')


def test_known_result(name, known_result_in_filename, known_result_out_filename):
    parse = import_module('surebet.parsing.' + name).parse

    known_result_in = read_sample(name, known_result_in_filename)
    known_result_out = read_sample(name, known_result_out_filename)

    if name == 'posit':
        parsing_result = try_parse(parse, known_result_in, name)
    else:  # bookmaker
        parsing_result = Bookmaker(name)
        try_parse(parse, known_result_in, name, bookmaker=parsing_result)
        parsing_result.format()

    assert obj_dumps(parsing_result) == json_dumps(known_result_out)

    logging.info('PASS: known result')
