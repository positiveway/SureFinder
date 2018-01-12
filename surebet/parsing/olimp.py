import lxml.html

from surebet.parsing import *
from surebet.parsing.bets import *

# table_rows = '//*[@id="champ_container_"]/table/'
# table_xpath = '//*[@id="champ_container_"]/table/tr[position() mod 2 = 0]/td/table'
# table_xpath = '//*[@id="champ_container_"]/table/tr'
table_xpath = '//*[@id="champ_container_"]/table/tbody/tr'

# bet_types = ['Tot', 'H2', 'H1', 'X2', '12', '1X', '2', 'X', '1']
bet_types = ['X2', '12', '1X', '2', 'X', '1']
# partbets_attribute_names = ['o1', 'ox', 'o2', 'o1x', 'o12', 'ox2']


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
    # print(html.xpath('//*[@id="champ_container_"]/table/tbody'))
    # exit()

    trs = xpath_with_check(html, table_xpath)
    if len(trs) % 2 != 0:
        raise ParseException('count of tr elements in {} should be even'.format(table_xpath))

    blocks = []
    for i in range(len(trs) // 2):
        blocks.append((trs[i * 2], trs[i * 2 + 1]))

    # sports = [block[0].xpath('td[1]/text()')[0] for block in blocks]

    for block in blocks:
        # each block has same sport name
        # print('=' * 50)
        # raw_sport_name = ''.join(block[0].xpath('td[1]/text()'))  # sport name
        raw_sport_name = ''.join(xpath_with_check(block[0], 'td[1]/text()'))  # sport name
        # print('Raw sport name:', raw_sport_name)
        sport_name = raw_sport_name.partition('.')[0].strip()
        # print('Sport name:', sport_name)
        # rows = block[1].xpath('td/table/tr')
        # rows = block[1].xpath('td/table/tbody/tr')
        rows = xpath_with_check(block[1], 'td/table/tbody/tr')
        if len(rows) % 2 != 0:
            raise ParseException('count of tr elements in {} should be even'.format('td/table/tbody/tr'))
        # print(rows)
        for i in range(len(rows) // 2):
            # current event
            teams_row, coefs_row = rows[i * 2], rows[i * 2 + 1]
            # teams_str = ''.join(teams_row.xpath('td[2]/font/b/span/text()'))  # teams
            teams_str = ''.join(xpath_with_check(teams_row, 'td[2]/font/b/span/text()'))  # teams
            # deleting prefix digits and punct
            teams_str = delete_prefix_digits_and_punct(teams_str.strip())
            teams_str = teams_str.strip()
            # print(teams_str)
            teams = teams_str.split(' - ')

            # team 1
            first_team = teams[0].strip()
            # print('First team:', first_team)
            # team 2
            second_team = teams[1].strip()
            # print('Second team:', second_team)
            # print(teams_row.xpath('td[2]/font/b/span/text()')[0])

            # getting coefficients
            # main bets
            nobrs = coefs_row.xpath('td/div/nobr')
            # nobrs = xpath_with_check(coefs_row, 'td/div/nobr')
            # print(nobrs)
            parts = []
            bets = get_main_coefs(nobrs)
            parts.append(bets)

            event = Event(first_team, second_team, parts)
            # adding to bookmaker
            if sport_name in bookmaker_sports:
                bookmaker_sports[sport_name].append(event)

    # for k, v in bookmaker_sports.items():
    #     print(k, '({}) :'.format(len(v)), v)

    # print(sports)
    # print(blocks[0][0].xpath('td[1]/text()')[0])

    # tables = xpath_with_check(html, table_xpath)
    # rows = [table.xpath('tr') for table in tables]
    # print(rows)

    # print(len(table))
    # print(table[0].get('class'))
    # inner_table = map(lambda x: x, table)

    return bookmaker


def get_main_coefs(nobrs):
    # if not nobrs:
    #     print('suspended')
    #  self.o1, self.ox, self.o2, self.o1x, self.o12, self.ox2
    # ['o1', 'ox', 'o2', 'o1x', 'o12', 'ox2']
    bets = PartBets()
    for nobr in nobrs:
        nobr_text = nobr.text.strip()
        nobr_text = nobr_text.partition(' ')[0].partition('(')[0]
        # print(nobr_text)
        if nobr_text in bet_types:
            attribute_name = 'o' + nobr_text.lower()
            coefficient = nobr.xpath('span')[0].get('data-v1')
            set_exist_attr(bets, attribute_name, parse_factor(coefficient))

    return bets


def delete_prefix_digits_and_punct(string):
    if not string:
        raise Exception('empty string')
    i = 0
    while i < len(string) and string[i].isdigit() or string[i] in '.,;:%#$^&*~`<>/?{}[]-+|':
        i += 1
    return string[i:]

def parse_sport(node):
    return xpath_with_check(node, './td[1]').text


def parse_event(node):
    header, bets_table = xpath_with_check(node, './td/table/tbody/tr')
