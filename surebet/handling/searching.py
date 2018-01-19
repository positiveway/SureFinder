from itertools import combinations

from surebet.handling import *
from surebet.handling.matching import match_sports
from surebet.handling.calculating import calc_surebets

from surebet.parsing.bets import CondBet

opposite_bets = {
    "o1": "o2",
    "o1x": "ox2",
}


def get_reversed_event(event):
    event.team1, event.team2 = event.team2, event.team1

    for part in event.parts:
        for bet in opposite_bets.keys():
            # part.o1, part.o2 = part.o2, part.o1
            temp = getattr(part, bet)
            setattr(part, bet, getattr(part, opposite_bets[bet]))
            setattr(part, opposite_bets[bet], temp)

        for hand_idx, hand in enumerate(part.hand):
            part.hand[hand_idx] = CondBet(-hand.cond, hand.v2, hand.v1)

        part.ind_total1, part.ind_total2 = part.ind_total2, part.ind_total1

    return event


def get_reversed_surebets(e_surebets):
    e_surebets.teams2 = [e_surebets.teams2[1], e_surebets.teams2[0]]

    for part_surebets in e_surebets.parts:
        for surebet in part_surebets.surebets:
            w2_name = surebet.w2.name
            if w2_name[0] == "o":  # if result bet
                for bet, opposite_bet in opposite_bets.items():
                    if w2_name == bet:
                        surebet.w2.name = opposite_bet
                    elif w2_name == opposite_bet:
                        surebet.w2.name = bet
            elif w2_name == "hand":
                surebet.w2.suffix = surebet.w1.suffix
            elif w2_name == "ind_total1" or w2_name == "ind_total2":
                surebet.w2.name = {
                    "ind_total1": "ind_total2",
                    "ind_total2": "ind_total1",
                }[w2_name]
    return e_surebets


def find_for_2_books(book1, book2):
    surebets = Surebets(book1.name, book2.name)

    sports = [attr for attr in book1.__dict__.keys() if attr != 'name']
    for sport_name in sports:
        sport1, sport2 = getattr(book1, sport_name), getattr(book2, sport_name)

        with_draw = sport_name not in ("tennis", "volley")
        for event_pair in match_sports(sport1, sport2):
            event1, event2 = event_pair.event1, event_pair.event2
            if event_pair.reversed_teams:
                event2 = get_reversed_event(event2)

            e_surebets = EventSurebets([event1.team1, event1.team2], [event2.team1, event2.team2])

            part_bets2 = {part_bets.part: part_bets for part_bets in event2.parts}
            for part_bets1 in event1.parts:
                part_num = part_bets1.part
                if part_num in part_bets2:
                    part_surebets = calc_surebets((part_bets1, part_bets2[part_num]), with_draw=with_draw)
                    if part_surebets:
                        e_surebets.parts.append(PartSurebets(part_surebets, part_num))

            if e_surebets.parts:
                if event_pair.reversed_teams:  # reverse second wagers in surebets
                    e_surebets = get_reversed_surebets(e_surebets)

                sport = getattr(surebets, sport_name)
                sport.append(e_surebets)

    return surebets


def find_surebets(bookmakers):
    bookmakers.format()

    all_surebets = []
    for book1, book2 in combinations(bookmakers.__dict__.values(), 2):
        all_surebets.append(find_for_2_books(book1, book2))

    return all_surebets
