from lxml import html

from surebet.parsing import *
from .bets import *

xp_event_id = '//table[@class="table-shortcuts-menu"]'

xp_blocks = '//*[contains(@id, "block")]'
xp_block_name = './table/tbody/tr/td[2]/div'
xp_part_block_name = './div[contains(@class, "name")]'

xp_details = './div[contains(@class, "table")]/div'
xp_detail_name = './table[1]/tbody/tr/td[2]/div'
xp_detail_rows = './table[2]/tr'

xp_row_cond = "./td[{}]/div/div[1]"
xp_row_factor = "./td[{}]/div/div[2]/span"

xp_closed_events = '//table[@data-sport-type="{}"]/tbody'
xp_win_bet = './tr[3]/td[@data-market-type="RESULT_2WAY"][{}]/div/span/span'


class EventInfo:
    def __init__(self, sport_name, name):
        self.sport_name = sport_name
        self.name = name


class WinBets:
    def __init__(self, o1, o2):
        self.o1 = o1
        self.o2 = o2


def factor_not_blocked(elem):
    return elem.get("class") != "igrey"


def get_factor(elem):
    return parse_factor(elem.get("data-selection-price"))


def get_cond(elem):
    return float(elem[1:-1])


def get_separator(event_name):
    return " @ " if "@" in event_name else " - "


def parse(site_info, bookmaker):
    sport_tree = get_sport_tree(site_info["sport_tree"])
    closed_events_bets = get_closed_events_bets(site_info["add_info"])

    for event_html in site_info["events"]:
        event_doc = html.fromstring(event_html)

        event_id = xpath_with_check(event_doc, xp_event_id)[0].get("data-tree-id")
        event_info = sport_tree[event_id]

        event = parse_event(event_doc, event_info)

        if event_id in closed_events_bets:
            event.parts[0].o1 = closed_events_bets[event_id].o1  # Closed events have bets only for part 0
            event.parts[0].o2 = closed_events_bets[event_id].o2

        sport_name = event_info.sport_name
        cur_sport = getattr(bookmaker, sport_name)
        cur_sport.append(event)


def get_sport_tree(raw_sport_tree):
    proper_names = {
        "Basketball": "basket",
        "Football": "soccer",
        "Ice Hockey": "hockey",
        "Tennis": "tennis",
        "Volleyball": "volley"
    }

    sport_tree = {}
    for sport in raw_sport_tree:
        sport_name = sport["name"]
        if sport_name not in proper_names:
            continue

        for event in sport["events"]:
            sport_tree[event["id"]] = EventInfo(proper_names[sport_name], event["name"])
    return sport_tree


def parse_event(event_doc, event_info):
    sport_name = event_info.sport_name

    main_part_details = []
    add_parts_block = None
    for block in xpath_with_check(event_doc, xp_blocks):
        block_name = get_text(xpath_with_check(block, xp_block_name)[0])
        block_type = get_block_type(sport_name, block_name)
        if block_type == 0:
            for detail in xpath_with_check(block, xp_details):
                main_part_details.append(detail)
        elif block_type == 1:
            add_parts_block = block

    parts = []
    event_name = event_info.name
    teams = parse_teams(event_name, get_separator(event_name))

    main_part_bets = handle_details(main_part_details, teams)
    main_part_bets.part = 0
    parts.append(main_part_bets)

    if add_parts_block is not None:
        add_parts_bets = handle_add_block(add_parts_block, teams)
        parts.extend(add_parts_bets)

    return Event(*teams, parts)


def get_block_type(sport_name, block_name):
    block_type = None
    for name in ("Main", "Handicap", "Total"):
        if name in block_name:
            block_type = 0
            break
    else:
        part_name = {
            "soccer": "Half",
            "basket": "Quarter",
            "hockey": "Period",
            "volley": "Set",
            "tennis": "Set",
        }[sport_name]
        if part_name in block_name:
            block_type = 1
    return block_type


def handle_details(details, teams):
    bets = PartBets()
    for detail in details:
        detail_name = get_text(xpath_with_check(detail, xp_detail_name)[0])

        handler_type = get_handler_type(detail_name)
        if handler_type == 0:
            for bet_name, factor in result_bets_handler(detail, teams):
                set_exist_attr(bets, bet_name, factor)
        elif handler_type == 1:
            cond_bet_type = get_cond_bet_type(detail_name, teams)
            cond_bets = cond_bet_handler(detail, cond_bet_type)

            bet_name = ("hand", "total", "ind_total1", "ind_total2")[cond_bet_type]
            set_exist_attr(bets, bet_name, cond_bets)

    return bets


def get_handler_type(detail_name):
    handler_type = None
    if "Total" in detail_name or "Handicap" in detail_name:
        excluded_names = ("Result", "Asian", "Sets")
        for name in excluded_names:
            if name in detail_name:
                break
        else:
            handler_type = 1
    elif "Result" in detail_name and _contain_part(detail_name) \
            or detail_name == "Result" or detail_name == "Normal Time Result":
        handler_type = 0
    return handler_type


def _contain_part(string):
    return contain_part(string, ("Quarter", "Half", "Set", "Period"), '\d.. {}')


def get_cond_bet_type(detail_name, teams):
    cond_bet_type = None
    for cur_type, name in enumerate(("Handicap", "Total", teams[0], teams[1])):
        if name in detail_name:
            cond_bet_type = cur_type
    if cond_bet_type is None:
        raise ParseException("got undefined cond bet")
    return cond_bet_type


def result_bets_handler(detail, teams):
    for row_node in xpath_with_check(detail, xp_detail_rows):
        row_name = get_text(xpath_with_check(row_node, "./td/div[1]")[0])
        bet_name = get_result_bet_name(row_name, *teams)

        factor_node = xpath_with_check(row_node, "./td/div[2]/span")[0]
        if factor_not_blocked(factor_node):
            yield bet_name, get_factor(factor_node)


def get_result_bet_name(row_name, team1, team2):
    outcomes = {
        "{} To Win".format(team1): "o1",
        "Draw": "ox",
        "{} To Win".format(team2): "o2",
        "{} To Win or Draw".format(team1): "o1x",
        "{} To Win or {} To Win".format(team1, team2): "o12",
        "{} To Win or Draw".format(team2): "ox2",
        team1: "o1",
        team2: "o2",
    }

    return outcomes[row_name]


def cond_bet_handler(detail, cond_bet_type):
    columns = [[], []]
    for row_node in xpath_with_check(detail, xp_detail_rows):
        row_header = row_node.xpath("./th[1]/div")
        if row_header:
            if get_text(row_header[0]) == "Odd":  # if odd/even header occurred
                break
            continue

        for cur_col in range(2):
            cond_node = xpath_with_check(row_node, xp_row_cond.format(cur_col + 1))[0]  # Xpath: numbering from 1
            cond = get_cond(get_text(cond_node))

            factor_node = xpath_with_check(row_node, xp_row_factor.format(cur_col + 1))[0]
            if factor_not_blocked(factor_node):
                columns[cur_col].append((cond, get_factor(factor_node)))

    cond_bets = []
    for first_value in columns[0]:
        cond = first_value[0]
        v1 = first_value[1]
        v2 = None

        cond_to_find = -cond if cond_bet_type == 0 else cond
        for second_value in columns[1]:
            if second_value[0] == cond_to_find:  # if found corresponding cond
                v2 = second_value[1]
                break
        if v2 is None:
            continue

        if cond_bet_type > 0:
            v1, v2 = v2, v1  # over and under have wrong order
        cond_bets.append(CondBet(cond, v1, v2))

    return cond_bets


def handle_add_block(add_block, teams):
    add_parts_bets = []
    for part_block in xpath_with_check(add_block, "./div"):
        part_block_node = xpath_with_check(part_block, xp_part_block_name)[0]
        part_block_name = get_text(part_block_node)
        part_num = int(part_block_name[0])

        add_bets = handle_details(xpath_with_check(part_block, xp_details), teams)
        add_bets.part = part_num
        add_parts_bets.append(add_bets)

    return add_parts_bets


def get_closed_events_bets(add_info):
    closed_events_bets = {}
    for sport_name in ("Tennis", "Volleyball"):
        if sport_name not in add_info:
            continue

        site_doc = html.fromstring(add_info[sport_name])

        events = site_doc.xpath(xp_closed_events.format(sport_name))
        for event_id, bets in handle_closed_events(events):
            closed_events_bets[event_id] = bets
    return closed_events_bets


def handle_closed_events(events):
    for event in events:
        event_id = event.get("data-event-treeid")

        win_bets = []
        for cur_bet in range(2):
            bet_node = event.xpath(xp_win_bet.format(cur_bet + 1))
            if bet_node and factor_not_blocked(bet_node[0]):
                win_bets.append(get_factor(bet_node[0]))
        if not win_bets:
            continue
        if len(win_bets) == 1:
            raise ParseException("found only one win bet in closed events")

        yield event_id, WinBets(*win_bets)
