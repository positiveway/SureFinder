import lxml.html

from surebet.parsing import *
from surebet.parsing.bets import *

table_rows = '//*[@id="champ_container_"]/table/tbody/tr'


def parse(source):
    html = lxml.html.fromstring(source)
    row_nodes = xpath_with_check(html, table_rows)

    bookmaker = Bookmaker()
    sports = {
        '1': bookmaker.soccer,
        '2': bookmaker.hockey,
        '3': bookmaker.basket,
        '4': bookmaker.tennis,
        '9': bookmaker.volley,
    }

    if len(row_nodes) % 2 != 0:
        StructureException('bets table')

    for idx in range(0, len(row_nodes), 2):
        sport = parse_sport(row_nodes[idx])


def parse_sport(node):
    return xpath_with_check(node, './td[1]').text


def parse_event(node):
    header, bets_table = xpath_with_check(node, './td/table/tbody/tr')
