import json
from os import path

from surebet.json_funcs import obj_dumps, json_dumps
from surebet.tests.handling import package_dir
from surebet.parsing.bets import Bookmakers
from surebet.parsing.fonbet import parse as fonbet_parse, parse_json as fonbet_parse_json
from surebet.parsing.marat import parse as marat_parse
from surebet.parsing.olimp import parse as olimp_parse
from surebet.handling.searching import find_surebets


def read_html(filename, site_name):
    with open(filename.format(site_name, 'html')) as f_html:
        result = f_html.read()
    return result


def read_json(filename, site_name):
    with open(filename.format(site_name, 'json')) as f_json:
        result = json.load(f_json)
    return result


def test_searching():
    filename_pattern = path.join(package_dir, 'searching', '{}.{}')
    fonbet_html = read_html(filename_pattern, 'fonbet')
    fonbet_json = read_json(filename_pattern, 'fonbet')
    marat_json = read_json(filename_pattern, 'marat')
    olimp_json = read_json(filename_pattern, 'olimp')

    bookmakers = Bookmakers()
    fonbet_parse(fonbet_html, bookmakers.fonbet)
    fonbet_parse_json(fonbet_json, bookmakers.fonbet)
    marat_parse(marat_json, bookmakers.marat)
    olimp_parse(olimp_json, bookmakers.olimp)

    surebets = find_surebets(bookmakers)
    surebets_known = read_json(filename_pattern, 'surebets')

    assert obj_dumps(surebets) == json_dumps(surebets_known)


test_searching()
