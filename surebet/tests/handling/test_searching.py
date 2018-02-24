import json
from os import path

from surebet.json_funcs import obj_dumps, json_dumps
from surebet.tests.handling import package_dir
from surebet.parsing.bets import Bookmakers
from surebet.parsing.fonbet import parse as fonbet_parse, parse_json as fonbet_parse_json
from surebet.parsing.marat import parse as marat_parse
from surebet.parsing.olimp import parse as olimp_parse
from surebet.handling.searching import find_surebets

FILENAME_PATTERN = path.join(package_dir, 'searching', '{}.{}')


def read_html(site_name):
    with open(FILENAME_PATTERN.format(site_name, 'html')) as f_html:
        result = f_html.read()
    return result


def read_json(site_name):
    with open(FILENAME_PATTERN.format(site_name, 'json')) as f_json:
        result = json.load(f_json)
    return result


def test_searching():
    fonbet_html = read_html('fonbet')
    fonbet_json = read_json('fonbet')
    marat_json = read_json('marat')
    olimp_json = read_json('olimp')

    bookmakers = Bookmakers()
    fonbet_parse(fonbet_html, bookmakers.fonbet)
    fonbet_parse_json(fonbet_json, bookmakers.fonbet)
    marat_parse(marat_json, bookmakers.marat)
    olimp_parse(olimp_json, bookmakers.olimp)

    surebets = find_surebets(bookmakers)
    surebets_known = read_json('surebets')

    assert obj_dumps(surebets) == json_dumps(surebets_known)
