from lxml import html
from re import match

from surebet import find_by_predicate
from surebet.converting import format_spaces
from surebet.handling import *
from surebet.handling.surebets import *
from surebet.parsing import *

xp_rows = '//table/tbody/tr[not(@id="")]'
none_factor = 0


def parse(source, all_surebets):
    books_surebets = {}
    for book_pair in all_surebets:
        books_surebets[(book_pair.book1, book_pair.book2)] = book_pair

    doc = html.fromstring(source)
    for row in xpath_with_check(doc, xp_rows):
        cols = xpath_with_check(row, "./td")

        book_pair = _get_book_pair(cols[2])
        is_reversed = book_names.index(book_pair[0]) > book_names.index(book_pair[1])
        if is_reversed:
            book_pair = tuple(reversed(book_pair))

        surebet = _get_surebet(cols[4], is_reversed)
        if not surebet:
            continue

        sport_name = _get_sport_name(cols[0])
        sport = getattr(books_surebets[book_pair], sport_name)

        events_teams = _get_events_teams(cols[3], is_reversed)
        e_surebets = find_by_predicate(sport, lambda ev: ev.teams1 == events_teams[0] and ev.teams2 == events_teams[1])
        if not e_surebets:
            e_surebets = EventSurebets(*events_teams)
            sport.append(e_surebets)

        part_num = _get_part_num(cols[4])
        part_surebets = find_by_predicate(e_surebets.parts, lambda part: part.part == part_num)
        if not part_surebets:
            part_surebets = PartSurebets([], part_num)
            e_surebets.parts.append(part_surebets)

        if surebet not in part_surebets.surebets:
            part_surebets.surebets.append(surebet)


def _get_sport_name(node):
    raw_name = xpath_with_check(node, "./a[not(@data-delay)]/img")[0].get("alt")
    return {
        "Soccer": "soccer",
        "Hockey": "hockey",
        "Basketball": "basket",
        "Tennis": "tennis",
        "Volleyball": "volley",
    }[raw_name]


def _get_book_pair(node):
    posit_names = {
        "fonbet": "fonbet",
        "marathon": "marat",
        "olimp": "olimp",
    }

    book1_name = get_text(xpath_with_check(node, "./a[1]")[0])
    book2_name = get_text(xpath_with_check(node, "./a[2]")[0])
    return posit_names[book1_name], posit_names[book2_name]


def _get_events_teams(node, is_reversed):
    name_nodes = xpath_with_check(node, './a[not(@rel="tooltip")]')
    if is_reversed:
        name_nodes = list(reversed(name_nodes))

    events_teams = []
    for name_node in name_nodes:
        name = format_spaces(get_text(name_node))
        events_teams.append(parse_teams(name, " vs "))

    return events_teams


def _get_part_num(node):
    part_num = 0
    node_text = get_text(xpath_with_check(node, "./nobr/a")[0])
    node_text = format_spaces(node_text)

    res = search(r"\((\d) [a-z]+\)", node_text)
    if res:
        part_num = int(res.group(1))
    return part_num


def _get_surebet(node, is_reversed):
    stake_nodes = xpath_with_check(node, "./nobr/a")
    if is_reversed:
        stake_nodes = list(reversed(stake_nodes))

    excluded_name = "inc OT"
    res_bet_patterns = {
        r"Win 1.*": "o1",
        r"1[^2].*": "o1",
        r"Win 2.*": "o2",
        r"2.*": "o2",
        r"X[^2].*": "ox",
        r"1X.*": "o1x",
        r"X2.*": "ox2",
        r"12.*": "o12",
    }
    cond_bet_patterns = {
        r"H(\d)\(([^\)]+)\).*": "hand",  # H1(1.5)
        r"(Under|Over)\(([^\)]+)\).*": "total",  # Under(1.5)
        r"T1 (Under|Over)\(([^\)]+)\).*": "ind_total1",  # T1 Under(1.5)
        r"T2 (Under|Over)\(([^\)]+)\).*": "ind_total2",  # T2 Under(1.5)
    }
    wagers = []
    for wager_num in range(2):
        stake_name = get_text(stake_nodes[wager_num]) + "$"  # adding $ for proper regexp matching
        stake_name = format_spaces(stake_name)
        if excluded_name in stake_name:
            continue

        wager_name = None
        for res_bet_pattern in res_bet_patterns:
            if match(res_bet_pattern, stake_name):
                wager_name = res_bet_patterns[res_bet_pattern]
                break
        if wager_name:
            wagers.append(Wager(wager_name, none_factor))
            continue

        found_wager = None
        for cond_bet_pattern in cond_bet_patterns:
            found_wager = match(cond_bet_pattern, stake_name)
            if found_wager:
                wager_name = cond_bet_patterns[cond_bet_pattern]
                break
        if wager_name:
            suffix = {
                "Over": "O",
                "Under": "U",
                "1": "1",
                "2": "2",
            }[found_wager.group(1)]
            cond = float(found_wager.group(2))

            wagers.append(CondWager(wager_name, none_factor, suffix, cond))

    surebet = None
    if len(wagers) == 2:
        surebet = Surebet(*wagers)
    return surebet
