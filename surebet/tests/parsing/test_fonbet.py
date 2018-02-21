import logging

from surebet.json_funcs import obj_dumps, json_dumps
from surebet.loading.fonbet import name
from surebet.tests.parsing import read_sample
from surebet.parsing.bets import Bookmaker
from surebet.parsing.fonbet import parse, parse_json

FILENAME_PATTERN = 'knownJSON{}'


def test_parse_json():
    sample_html = read_sample(name, FILENAME_PATTERN.format('.html'))
    sample_json = read_sample(name, FILENAME_PATTERN.format('.json'))

    bookmaker = Bookmaker(name)
    parse(sample_html, bookmaker)
    parse_json(sample_json, bookmaker)

    result = read_sample(name, FILENAME_PATTERN.format('result.json'))
    assert json_dumps(result) == obj_dumps(bookmaker)

    logging.info('PASS: known result')
