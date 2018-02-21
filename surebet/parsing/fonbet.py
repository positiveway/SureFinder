import lxml.html

from surebet.parsing import *
from surebet.parsing.bets import *

table_rows = '//table[@id="lineTable"]/tbody/tr'
ev_name = './/td[contains(@class, "eventCellName")]/div[contains(@id, "event")]'
SCORE = './td[contains(@class, "eventCellName")]/div[contains(@class, "eventDataWrapper")]/div[contains(@class, ' \
        '"eventScore")] '
grid = './/div[@class="detailsDIV"]/table'

tr_event = "trEvent"
tr_event_child = "trEventChild"
tr_event_details = "trEventDetails"

hand_ids = [0, 1, 3]
total_ids = [0, 1, 2]

FACTORS_DICT = {'hand': {1: [927, 937, 1845], 2: [928, 938, 1846]},
                'total': {1: [930, 940, 1848], 2: [931, 941, 1849]},
                'o1': [921, 3150, 3144],
                'o2': [923, 3151, 3145],
                'o12': [1571],
                'o1x': [924],
                'ox2': [925],
                'ox': [922, 3152]
                }


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

    name = None
    is_not_blocked = False
    if len(name_node) > 1:
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
    score_node = xpath_with_check(row_node, SCORE)[0]
    full_score = get_text(score_node).partition(" ")[0]
    score = full_score.partition(" ")[0]  # first part of score is needed

    attr = row_node.get("id")
    event_id = attr.strip()[5:]

    bets = FonbetPartBets(score, event_id)

    col_nodes = xpath_with_check(row_node, './/td')

    for idx, bet in enumerate(['o1', 'ox', 'o2', 'o1x', 'o12', 'ox2']):
        text = col_nodes[idx + 3].text
        if text:
            set_exist_attr(bets, bet, CustomBet(parse_factor(text)))

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

    factor_ids = []
    for id in ids[1:]:  # skip first node (stands for bet condition)
        attr = nodes[id].get("id")
        factor_id = attr.partition("f")[2]
        factor_ids.append(factor_id)

    return CustomCondBet(*factors, *factor_ids)


def parse_json(line, bookmaker):
    events_to_factors = {event['id']: set() for event in line['events']}
    for factor in line['customFactors']:
        events_to_factors[factor['e']].add(factor['f'])

    parts_to_check = []
    for sport in bookmaker.attrs_dict():
        for obj_event in getattr(bookmaker, sport):
            for part in obj_event.parts:
                if int(part.event_id) in events_to_factors:
                    parts_to_check.append(part)

    for part in parts_to_check:
        bet_types = [(bet_type, getattr(part, bet_type)) for bet_type in ['hand', 'total']]
        for bet_name, bet_list in bet_types:
            for bet in bet_list:
                handle_json_bet(bet_name, bet, events_to_factors[int(part.event_id)])

        bet_types = [(bet_type, getattr(part, bet_type)) for bet_type in ['o1', 'ox', 'o2', 'o1x', 'o12', 'ox2']]
        for bet_name, bet in bet_types:
            handle_json_bet(bet_name, bet, events_to_factors[int(part.event_id)])


def handle_json_bet(bet_name, bet, factors):
    if isinstance(bet, CustomCondBet):
        if not bet.v1_id:
            bet.v1_id = get_factor(factors, FACTORS_DICT[bet_name][1])
        if not bet.v2_id:
            bet.v2_id = get_factor(factors, FACTORS_DICT[bet_name][2])
    elif isinstance(bet, CustomBet):
        if not bet.factor_id:
            bet.factor_id = get_factor(factors, FACTORS_DICT[bet_name])


def get_factor(factors, factors_set):
    for factor in factors_set:
        if factor in factors:
            return factor
    return ''
