import re

from surebet.parsing import *
from surebet.parsing.bets import *

TOTAL_INFO_KEYS = ['on', 'i', 'p', 'v']
HANDICAP_INFO_KEYS = ['on', 'p', 'v']


class Total:
    def __init__(self):
        self._type = self._id = ''
        self._step = self.cond = self.coef = 0

    def add(self, _id, _type, cond, coef):
        if not (len(_type) == 1 and _type in 'OU'):
            raise ParseException('Unknown total type "{}" '
                                 '(id: "{}", cond: "{}", coef: "{}").'.format(_type, _id, cond, coef))
        if self._step == 0:
            self.fill(_id, _type, cond, coef)
            self._step = 1
        elif self._step == 1:
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
        self._id = ''
        self._step = self.team = self.cond = self.coef = 0

    def add(self, _id, team, cond, coef):
        if self._step == 0:
            self.fill(_id, team, cond, coef)
            self._step = 1
        elif self._step == 1:
            if _id == self._id and team != self.team and cond == -self.cond:
                v1, v2 = coef, self.coef
                if cond >= 0:
                    cond = -cond
                    v1, v2 = v2, v1
                self.clear()
                return CondBet(cond, v1, v2)
            else:  # error
                self.fill(_id, team, cond, coef)

    def fill(self, _id, team, cond, coef):
        self._id = _id
        self.team = team
        self.cond = cond
        self.coef = coef

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
            # print('{} VS {}'.format(first_team, second_team))

            event_data = event['it']
            parts = []
            main_bets = PartBets()
            for bets_part in event_data:
                bets_part_name = bets_part['n']
                if bets_part_name == 'Main Bets':
                    bets = bets_part['i']
                    hand = Handicap()
                    total = Total()

                    for bet in bets:
                        bet_type = bet['on']
                        coef = float(bet['v'])
                        if bet_type == 'П1':  # 1
                            main_bets.o1 = coef
                        elif bet_type == 'П2':  # 2
                            main_bets.o2 = coef
                        elif bet_type == 'Х':  # X
                            main_bets.ox = coef
                        elif bet_type == '1Х':  # 1X
                            main_bets.o1x = coef
                        elif bet_type == '12':  # 12
                            main_bets.o12 = coef
                        elif bet_type == 'Х2':  # X2
                            main_bets.ox2 = coef
                        elif bet_type == 'Ф1' or bet_type == 'Ф2':  # H1 and H2
                            info = HandicapInfo(bet)
                            cond_bet = hand.add(info.id, info.team, info.cond, info.coef)
                            if cond_bet:
                                main_bets.hand.append(cond_bet)
                        elif bet_type == 'Тот':  # Tot
                            info = TotalInfo(bet)
                            cond_bet = total.add(info.id, info.type, info.cond, info.coef)
                            if cond_bet:
                                main_bets.total.append(cond_bet)
                elif bets_part_name == 'Individual total':  # only soccer
                    if sport_name == 'soccer':
                        bets = bets_part['i']
                        total = Total()

                        for bet in bets:
                            info = TotalInfo(bet)
                            cond_bet = total.add(info.id, info.type, info.cond, info.coef)
                            if cond_bet:
                                ind_total = main_bets.ind_total1 if info.team == 1 else main_bets.ind_total2
                                ind_total.append(cond_bet)
                elif bets_part_name == 'Points':  # only basket (individual total)
                    if sport_name == 'basket':
                        bets = bets_part['i']
                        total = Total()
                        for bet in bets:
                            info = TotalInfo(bet)
                            cond_bet = total.add(info.id, info.type, info.cond, info.coef)
                            if cond_bet:
                                ind_total = main_bets.ind_total1 if info.team == 1 else main_bets.ind_total2
                                ind_total.append(cond_bet)
                elif bets_part_name == 'Additional total':
                    bets = bets_part['i']
                    total = Total()

                    for bet in bets:
                        info = TotalInfo(bet)
                        cond_bet = total.add(info.id, info.type, info.cond, info.coef)
                        if cond_bet:
                            main_bets.total.append(cond_bet)
                elif bets_part_name == 'Additional handicap' or bets_part_name == 'Handicap':
                    bets = bets_part['i']
                    hand = Handicap()

                    for bet in bets:
                        info = HandicapInfo(bet)
                        cond_bet = hand.add(info.id, info.team, info.cond, info.coef)
                        if cond_bet:
                            main_bets.hand.append(cond_bet)

            parts.append(main_bets)

            # quarter, period, set
            # TODO Goals, Bets by sets

            for bets_part in event_data:
                bets_part_name = bets_part['n']
                if bets_part_name == 'Quarters outcome':  # basket
                    # Ч3П1 Ч3Н Ч3П2 Ч3П1Ф0 Ч3П2Ф0 Ч3Ф1 Ч3Ф2 Ч3Тот
                    bets = bets_part['i']
                    if bets:
                        quarter_bets = get_part_bets(parts, int(bets[0]['on'][1]))
                        hand = Handicap()
                        total = Total()

                        for bet in bets:
                            bet_name = bet['on']
                            coef = float(bet['v'])
                            if bet_name[-2:] == 'П1':  # 1
                                quarter_bets.o1 = coef
                            elif bet_name[-2:] == 'П2':  # 2
                                quarter_bets.o2 = coef
                            elif bet_name[-1] == 'Н':  # X
                                quarter_bets.ox = coef
                            elif bet_name[-3:] == 'Тот':
                                info = TotalInfo(bet)
                                cond_bet = total.add(info.id, info.type, info.cond, info.coef)
                                if cond_bet:
                                    quarter_bets.total.append(cond_bet)
                            elif bet_name[-2:] == 'Ф1' or bet_name[-2:] == 'Ф2':  # H1 and H2
                                info = HandicapInfo(bet)
                                cond_bet = hand.add(info.id, info.team, info.cond, info.coef)
                                if cond_bet:
                                    quarter_bets.hand.append(cond_bet)
                elif re.match(r'^[0-9] period: Periods outcome', bets_part_name):  # hockey
                    # П3П1 П3Н П3П2 П31Х П312 П3Х2 П3Ф1 П3Ф2 П3Тот
                    bets = bets_part['i']
                    if bets:
                        period_bets = get_part_bets(parts, int(bets[0]['on'][1]))
                        hand = Handicap()
                        total = Total()

                        for bet in bets:
                            bet_name = bet['on']
                            coef = float(bet['v'])
                            if bet_name[-2:] == 'П1':
                                period_bets.o1 = coef
                            elif bet_name[-1] == 'Н':
                                period_bets.ox = coef
                            elif bet_name[-2:] == 'П2':
                                period_bets.o2 = coef
                            elif bet_name[-2:] == '1Х':
                                period_bets.o1x = coef
                            elif bet_name[-2:] == '12':
                                period_bets.o12 = coef
                            elif bet_name[-2:] == 'Х2':
                                period_bets.ox2 = coef
                            elif bet_name[-2:] == 'Ф1' or bet_name[-2:] == 'Ф2':
                                info = HandicapInfo(bet)
                                cond_bet = hand.add(info.id, info.team, info.cond, info.coef)
                                if cond_bet:
                                    period_bets.hand.append(cond_bet)
                            elif bet_name[-3:] == 'Тот':
                                info = TotalInfo(bet)
                                cond_bet = total.add(info.id, info.type, info.cond, info.coef)
                                if cond_bet:
                                    period_bets.total.append(cond_bet)
                elif re.match(r'^[0-9] period: Individual total', bets_part_name):  # hockey
                    # П3К1 П3К2
                    bets = bets_part['i']
                    if bets:
                        period_bets = get_part_bets(parts, int(bets[0]['on'][1]))
                        total = Total()

                        for bet in bets:
                            info = TotalInfo(bet)
                            cond_bet = total.add(info.id, info.type, info.cond, info.coef)
                            if cond_bet:
                                ind_total = period_bets.ind_total1 if info.team == 1 else period_bets.ind_total2
                                ind_total.append(cond_bet)
                elif re.match(r'^[0-9] period: Additional total', bets_part_name):  # hockey
                    # П3Тот2
                    bets = bets_part['i']
                    if bets:
                        period_bets = get_part_bets(parts, int(bets[0]['on'][1]))
                        total = Total()

                        for bet in bets:
                            info = TotalInfo(bet)
                            cond_bet = total.add(info.id, info.type, info.cond, info.coef)
                            if cond_bet:
                                period_bets.total.append(cond_bet)
                elif bets_part_name == 'Bets by sets':  # tennis
                    # С2П1 С2П2 С2_Ф1_-3.5 С2_Ф2_3.5 С2_Ф1_-2.5 С2_Ф2_2.5 С2_Ф1_-1.5 С2_Ф2_1.5
                    # С2Тот С2Тот С2Тот2 С2Тот2 С2Тот3 С2Тот3
                    # sample0.json | Women. ITF Tournament. Midland. Hard. Qualification | Mateas M. VS Scholl Ch.
                    pass

            bookmaker_sports[sport_name].append(Event(first_team, second_team, parts))

    return bookmaker


def get_part_bets(parts, part):
    for part_bets in parts:
        if part_bets.part == part:
            return part_bets
    part_bets = PartBets()
    part_bets.part = part
    parts.append(part_bets)
    return part_bets
