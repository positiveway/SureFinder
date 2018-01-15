import lxml.html
import re

from surebet.parsing import *
from surebet.parsing.bets import *

# table_xpath = '//*[@id="champ_container_"]/table/tr[position() mod 2 = 0]/td/table'
BLOCKS_XPATH = '//*[@id="champ_container_"]/table/tr'
BLOCK_BODY_ROWS_XPATH = 'td/table/tr'
RAW_SPORT_NAME_XPATH = 'td[1]/text()'
TEAMS_STR_XPATH = 'td[2]/font/b/span/text()'
MAIN_BETS_ROWS_XPATH = 'td/div/nobr'
OTHER_BETS_XPATH = 'td/div/div/*'

BET_TYPES = ['X2', '12', '1X', '2', 'X', '1']  # ['Tot', 'H2', 'H1']

DOUBLE_PARENTHESES_REGEXP = r'^.*\(.*\) - .*\(.*\).*$'
PARENTHESES_REGEXP = r'^.*\(.*\).*$'


def parse(source):
    bookmaker = Bookmaker()
    bookmaker_sports = {
        'Soccer': bookmaker.soccer,
        'Ice Hockey': bookmaker.hockey,
        'Basketball': bookmaker.basket,
        'Tennis': bookmaker.tennis,
        'Volleyball': bookmaker.volley,
    }

    html = lxml.html.fromstring(source)

    rows = xpath_with_check(html, BLOCKS_XPATH)
    if len(rows) % 2 != 0:
        raise ParseException('count of tr elements in {} should be even'.format(BLOCKS_XPATH))

    blocks = []
    for i in range(len(rows) // 2):
        blocks.append((rows[i * 2], rows[i * 2 + 1]))

    for block_head, block_body in blocks:
        # each block has same sport name
        raw_sport_name = ''.join(xpath_with_check(block_head, RAW_SPORT_NAME_XPATH))
        sport_name = raw_sport_name.partition('.')[0].strip()
        if sport_name not in bookmaker_sports:
            continue

        block_body_rows = xpath_with_check(block_body, BLOCK_BODY_ROWS_XPATH)
        if len(block_body_rows) % 2 != 0:
            raise ParseException('count of tr elements in {} should be even'.format(BLOCK_BODY_ROWS_XPATH))

        for i in range(len(block_body_rows) // 2):
            # current event
            teams_row, coefficients_row = block_body_rows[i * 2], block_body_rows[i * 2 + 1]

            teams_str = ''.join(xpath_with_check(teams_row, TEAMS_STR_XPATH))
            first_team, second_team = get_teams(teams_str)

            # getting coefficients
            parts = []
            # main bets
            main_bets_rows = coefficients_row.xpath(MAIN_BETS_ROWS_XPATH)  # main_bets_rows may be []
            bets = get_main_bets(main_bets_rows)
            # other bets
            other_bets_rows = coefficients_row.xpath(OTHER_BETS_XPATH)
            bets.ind_total1, bets.ind_total2 = get_individual_totals(other_bets_rows, first_team, second_team)

            parts.append(bets)

            bookmaker_sports[sport_name].append(Event(first_team, second_team, parts))

    return bookmaker


def get_main_bets(main_bets_rows):
    # if main_bets_rows == []:
    #     print('suspended')
    # ['o1', 'ox', 'o2', 'o1x', 'o12', 'ox2']
    bets = PartBets()
    for row in main_bets_rows:
        bet_type = row.text.strip().partition(' ')[0].partition('(')[0]
        span = xpath_with_check(row, 'span')[0]

        # X2, 12, 1X, 2, X, 1
        if bet_type in BET_TYPES:
            attribute_name = 'o' + bet_type.lower()
            set_exist_attr(bets, attribute_name, parse_factor(span.get('data-v1')))

        # Total
        if bet_type == 'Tot':
            bets.total.append(CondBet(parse_factor(span.get('data-v1')),
                                      parse_factor(span.get('data-v3')),
                                      parse_factor(span.get('data-v2'))))

        # Handicap
        if bet_type == 'H1':
            bets.hand.append(CondBet(parse_factor(span.get('data-v1')),
                                     parse_factor(span.get('data-v2')),
                                     0.0))

        if bet_type == 'H2':
            if bets.hand:
                bets.hand[0].v2 = parse_factor(span.get('data-v2'))

    return bets


def get_individual_totals(other_bets_rows, first_team, second_team):
    ind_total1, ind_total2 = [], []
    bet_type = ''
    for row in other_bets_rows:
        if row.tag == 'b':
            bet_type = xpath_with_check(row, 'i')[0].text.strip()
        if row.tag == 'nobr':
            if bet_type == 'Individual total:':
                team = row.text.rpartition('(')[0].strip()
                span = xpath_with_check(row, 'span')[0]
                cond_bet = CondBet(parse_factor(span.get('data-v1')),
                                   parse_factor(span.get('data-v2')),
                                   parse_factor(span.get('data-v3')))
                if team == first_team:
                    ind_total1.append(cond_bet)
                elif team == second_team:
                    ind_total2.append(cond_bet)
                else:
                    raise ParseException('Undefined team "{}". First: "{}". Second: "{}"'.format(team, first_team,
                                                                                                 second_team))

    return ind_total1, ind_total2


def get_teams(teams_str):
    # '  International - RS (U19) - EC XV De Novembro Jau SP (U19)'
    teams_str = delete_prefix_number(teams_str.strip())
    teams_str_parts = tuple(map(lambda s: s.strip(), teams_str.split(' - ')))
    if len(teams_str_parts) == 2:
        return teams_str_parts

    matches_double_parentheses = bool(re.match(DOUBLE_PARENTHESES_REGEXP, teams_str))  # *(*) - *(*)
    if matches_double_parentheses:
        for i in range(1, len(teams_str_parts)):
            first_team, second_team = ' - '.join(teams_str_parts[:i]), ' - '.join(teams_str_parts[i:])
            if re.match(PARENTHESES_REGEXP, first_team) and re.match(PARENTHESES_REGEXP, second_team):
                return first_team, second_team

    raise ParseException('Teams string parsing error. Raw : "{}". Handled: "{}".'.format(teams_str, teams_str_parts))


def delete_prefix_number(string):
    if not string:
        raise ParseException('Empty string')
    result = re.match(r'^[0-9]+\.', string)
    return string[result.end():] if result else string
