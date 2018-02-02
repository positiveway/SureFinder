import re

from surebet.parsing import *
from surebet.parsing.bets import *

TOTAL_INFO_KEYS = ['on', 'i', 'p', 'v']
HANDICAP_INFO_KEYS = ['on', 'p', 'v']

PART_BETS_ATTR = {
    'П1': 'o1',
    'П2': 'o2',
    'Х': 'ox',
    '1Х': 'o1x',
    '12': 'o12',
    'Х2': 'ox2',
}

HANDICAP_TYPES = ['Ф1', 'Ф2']


class Total:
    def __init__(self):
        self._type = self._id = ''
        self.cond = self.coef = 0
        self.filled = False

    def add(self, _id, _type, cond, coef):
        if not (len(_type) == 1 and _type in 'OU'):
            raise ParseException('Unknown total type "{}" '
                                 '(id: "{}", cond: "{}", coef: "{}").'.format(_type, _id, cond, coef))
        if not self.filled:
            self.fill(_id, _type, cond, coef)
        else:
            if _id == self._id and _type != self._type and cond == self.cond:
                v1, v2 = self.coef, coef
                if _type == 'O':
                    v1, v2 = v2, v1
                self.clear()
                return CondBet(cond, v1, v2)
            else:  # error
                self.fill(_id, _type, cond, coef)

    def fill(self, _id, _type, cond, coef):
        self._id = _id
        self._type = _type
        self.cond = cond
        self.coef = coef
        self.filled = True

    def clear(self):
        self.__init__()


class TotalInfo:
    def __init__(self, bet):
        for key in TOTAL_INFO_KEYS:
            if key not in bet:
                raise StructureException('There is no key "{}" in bet: "{}".'.format(key, bet))
        self.id = bet['on']
        self.type = bet['i'][-1]
        self.cond = float(bet['p'])
        self.coef = float(bet['v'])
        self.team = 0
        team_char = bet['on'][-1]
        if team_char.isdigit():
            self.team = int(team_char)


class Handicap:
    def __init__(self):
        self.first_id = ''
        self.first_team = self.first_cond = self.first_coef = 0
        self.filled = False

    def add(self, _id, team, cond, coef):
        if not self.filled:
            self.fill(_id, team, cond, coef)
        else:
            if _id == self.first_id and team != self.first_team and cond == -self.first_cond:
                if self.first_team == 1:
                    cond1, v1, v2 = self.first_cond, self.first_coef, coef
                else:
                    cond1, v1, v2 = cond, coef, self.first_coef
                self.clear()
                return CondBet(cond1, v1, v2)
            else:  # error
                self.fill(_id, team, cond, coef)

    def fill(self, _id, team, cond, coef):
        self.first_id = _id
        self.first_team = team
        self.first_cond = cond
        self.first_coef = coef
        self.filled = True

    def clear(self):
        self.__init__()


class HandicapInfo:
    def __init__(self, bet):
        for key in HANDICAP_INFO_KEYS:
            if key not in bet:
                raise StructureException('There is no key "{}" in bet: "{}".'.format(key, bet))
        self.id = bet['on'][:-1]
        self.cond = float(bet['p'])
        self.coef = float(bet['v'])
        self.team = int(bet['on'][-1])


def parse(json, bookmaker):
    bookmaker_sports = {
        'soccer': bookmaker.soccer,
        'hockey': bookmaker.hockey,
        'basket': bookmaker.basket,
        'tennis': bookmaker.tennis,
        'volley': bookmaker.volley,
    }

    for sport_name, events in json.items():
        for event in events:
            first_team = event['c1']
            second_team = event['c2']

            event_data = event['it']
            parts = [parse_main_bets(event_data, sport_name)]
            parse_other_bets(event_data, parts)  # quarter, period, set

            bookmaker_sports[sport_name].append(Event(first_team, second_team, parts))

    return bookmaker


def parse_main_bets(event_data, sport_name):
    main_bets = PartBets()
    for bets_part in event_data:
        bets_part_name = bets_part['n']
        bets = bets_part['i']

        hand = Handicap()
        total = Total()

        if bets_part_name == 'Main Bets':
            for bet in bets:
                bet_type = bet['on']
                if bet_type in PART_BETS_ATTR:
                    set_exist_attr(main_bets, PART_BETS_ATTR[bet_type], float(bet['v']))
                elif bet_type in HANDICAP_TYPES:  # H1 and H2
                    add_handicap(bet, hand, main_bets)
                elif bet_type == 'Тот':  # Tot
                    add_total(bet, total, main_bets)
        elif bets_part_name == 'Individual total':  # only soccer
            if sport_name == 'soccer':
                for bet in bets:
                    add_ind_total(bet, total, main_bets)
        elif bets_part_name == 'Points':  # only basket (individual total)
            if sport_name == 'basket':
                for bet in bets:
                    add_ind_total(bet, total, main_bets)
        elif bets_part_name == 'Additional total':
            for bet in bets:
                add_total(bet, total, main_bets)
        elif bets_part_name == 'Additional handicap' or bets_part_name == 'Handicap':
            for bet in bets:
                add_handicap(bet, hand, main_bets)

    return main_bets


def parse_other_bets(event_data, parts):
    # TODO Bets by sets, Goals
    for bets_part in event_data:
        bets_part_name = bets_part['n']
        bets = bets_part['i']
        if not bets:    # for part number
            continue

        hand = Handicap()
        total = Total()

        if bets_part_name == 'Quarters outcome':  # basket
            # Ч3П1 Ч3Н Ч3П2 Ч3П1Ф0 Ч3П2Ф0 Ч3Ф1 Ч3Ф2 Ч3Тот
            quarter_bets = get_part_bets(parts, int(bets[0]['on'][1]))

            for bet in bets:
                bet_type = bet['on']
                coef = float(bet['v'])
                if bet_type[-1] == 'Н':
                    quarter_bets.ox = coef
                elif bet_type[-2:] in PART_BETS_ATTR:    # П1 П2
                    set_exist_attr(quarter_bets, PART_BETS_ATTR[bet_type[-2:]], coef)
                elif bet_type[-2:] in HANDICAP_TYPES:
                    add_handicap(bet, hand, quarter_bets)
                elif bet_type[-3:] == 'Тот':
                    add_total(bet, total, quarter_bets)
        elif re.match(r'^[0-9] period: Periods outcome', bets_part_name):  # hockey
            # П3П1 П3Н П3П2 П31Х П312 П3Х2 П3Ф1 П3Ф2 П3Тот
            period_bets = get_part_bets(parts, int(bets[0]['on'][1]))

            for bet in bets:
                bet_type = bet['on']
                coef = float(bet['v'])
                if bet_type[-1] == 'Н':
                    period_bets.ox = coef
                elif bet_type[-2:] in PART_BETS_ATTR:    # П1 П2
                    set_exist_attr(period_bets, PART_BETS_ATTR[bet_type[-2:]], coef)
                elif bet_type[-2:] in HANDICAP_TYPES:
                    add_handicap(bet, hand, period_bets)
                elif bet_type[-3:] == 'Тот':
                    add_total(bet, total, period_bets)
        elif re.match(r'^[0-9] period: Individual total', bets_part_name):  # hockey
            # П3К1 П3К2
            period_bets = get_part_bets(parts, int(bets[0]['on'][1]))

            for bet in bets:
                add_ind_total(bet, total, period_bets)
        elif re.match(r'^[0-9] period: Additional total', bets_part_name):  # hockey
            # П3Тот2
            period_bets = get_part_bets(parts, int(bets[0]['on'][1]))

            for bet in bets:
                add_total(bet, total, period_bets)
        elif bets_part_name == 'Bets by sets':  # tennis
            # С2П1 С2П2 С2_Ф1_-3.5 С2_Ф2_3.5 С2_Ф1_-2.5 С2_Ф2_2.5 С2_Ф1_-1.5 С2_Ф2_1.5
            # С2Тот С2Тот С2Тот2 С2Тот2 С2Тот3 С2Тот3
            # sample0.json | Women. ITF Tournament. Midland. Hard. Qualification | Mateas M. VS Scholl Ch.
            pass


def get_part_bets(parts, part):
    for part_bets in parts:
        if part_bets.part == part:
            return part_bets
    part_bets = PartBets()
    part_bets.part = part
    parts.append(part_bets)
    return part_bets


def get_part_bets_attr(bet_type_str):
    if bet_type_str[-1] == 'Н' or len(bet_type_str) == 1 and bet_type_str[-1] == 'Х':
        return 'ox'

    two_last_chars = bet_type_str[-2:]
    if two_last_chars in PART_BETS_ATTR:
        return PART_BETS_ATTR[two_last_chars]

    if two_last_chars in HANDICAP_TYPES:
        return 'hand'

    if bet_type_str[-3:] == 'Тот':
        return 'total'


def add_handicap(bet, hand, part_bets):
    info = HandicapInfo(bet)
    cond_bet = hand.add(info.id, info.team, info.cond, info.coef)
    if cond_bet:
        part_bets.hand.append(cond_bet)


def add_total(bet, total, part_bets):
    info = TotalInfo(bet)
    cond_bet = total.add(info.id, info.type, info.cond, info.coef)
    if cond_bet:
        part_bets.total.append(cond_bet)


def add_ind_total(bet, total, part_bets):
    info = TotalInfo(bet)
    cond_bet = total.add(info.id, info.type, info.cond, info.coef)
    if cond_bet:
        ind_total = part_bets.ind_total1 if info.team == 1 else part_bets.ind_total2
        ind_total.append(cond_bet)
