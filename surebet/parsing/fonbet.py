import lxml.html

from surebet.parsing import *
from .bets import *

table_rows = '//table[@id="lineTable"]/tbody/tr'
ev_name = './/td[contains(@class, "eventCellName")]/div[contains(@id, "event")]'
grid = './/div[@class="detailsDIV"]/table'

tr_event = "trEvent"
tr_event_child = "trEventChild"
tr_event_details = "trEventDetails"

hand_ids = [0, 1, 3]
total_ids = [0, 1, 2]


class RowInfo:
    def __init__(self, ev_class, node):
        self.ev_class = ev_class
        self.node = node


def parse(source, bookmaker):
    html = lxml.html.fromstring(source)
    row_nodes = xpath_with_check(html, table_rows)

    sports = {
        '1': bookmaker.soccer,
        '2': bookmaker.hockey,
        '3': bookmaker.basket,
        '4': bookmaker.tennis,
        '9': bookmaker.volley,
    }

    rows_info = []
    prev_sport = None
    for row_node in row_nodes:
        row_classes = row_node.get('class').split(" ")
        if len(row_classes) == 1:
            continue
        if len(row_classes) != 3:
            raise ParseException('attribute @class not found')

        sport_num = row_classes[1][10:]

        if sport_num not in sports.keys():
            continue

        row_class = row_classes[0]
        if row_class == tr_event:
            append_event(rows_info, prev_sport)

            prev_sport = sports[sport_num]
            rows_info.clear()

        rows_info.append(RowInfo(row_class, row_node))

    append_event(rows_info, prev_sport)


def append_event(rows_info, sport):
    if rows_info:
        sport.append(parse_event(rows_info))


def parse_event(rows_info):
    node = rows_info[0].node
    name, is_not_blocked = get_event_info(node)
    teams = parse_teams(name, '—')

    parts = []
    bets = None
    if is_not_blocked:
        bets = handle_row(node)
        bets.part = 0

    for row_info in rows_info[1:]:
        ev_class, node = row_info.ev_class, row_info.node

        if ev_class == tr_event_details:
            if bets:
                for bet_name, val in parse_event_details(node):
                    getattr(bets, bet_name).append(val)

        elif ev_class == tr_event_child:
            if bets:
                parts.append(bets)

            name, is_not_blocked = get_event_info(node)

            bets = None
            if is_not_blocked and contain_part(name, ('half', 'quarter', 'set', 'period')):
                bets = handle_row(node)
                part_num = int(name[0])
                bets.part = part_num

    if bets:
        parts.append(bets)

    return Event(*teams, parts)


def get_event_info(row_node):
    title = xpath_with_check(row_node, ev_name)
    name_node = xpath_with_check(title[0], './/text()')

    name = name_node[1].strip()
    is_not_blocked = title[0].get('class') != 'eventBlocked'

    return name, is_not_blocked


def parse_event_details(node):
    grid_nodes = xpath_with_check(node, grid)

    allowed = {
        'Hcap': 'hand',
        'Totals': 'total',
        'Team Totals-1': 'ind_total1',
        'Team Totals-2': 'ind_total2',
    }

    for grid_node in grid_nodes:
        caption_node = xpath_with_check(grid_node, './/thead/tr[1]/th/text()')
        _caption = caption_node[0].strip()

        caption = allowed.get(_caption, None)
        if not caption:
            continue

        grid_rows = xpath_with_check(grid_node, './/tbody/tr')

        for grid_row in grid_rows:
            grid_cols = xpath_with_check(grid_row, './/td')

            ids = hand_ids if caption == 'hand' else total_ids
            cond_bet = handle_cond_bet(grid_cols, ids)

            yield caption, cond_bet


def handle_row(row_node):
    bets = PartBets()

    col_nodes = xpath_with_check(row_node, './/td')

    for idx, bet in enumerate(['o1', 'ox', 'o2', 'o1x', 'o12', 'ox2']):
        text = col_nodes[idx + 3].text
        if text:
            set_exist_attr(bets, bet, parse_factor(text))

    hand = handle_cond_bet(col_nodes[9:13], hand_ids)
    bets.hand.append(hand)

    total = handle_cond_bet(col_nodes[13:16], total_ids)
    bets.total.append(total)

    return bets


def handle_cond_bet(nodes, ids):
    if ids[-1] >= len(nodes):
        return None

    factors = []
    for id in ids:
        text = nodes[id].text
        if text:
            factors.append(parse_factor(text))

    if len(factors) != 3:
        return None

    return CondBet(*factors)
