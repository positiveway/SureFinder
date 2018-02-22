from surebet.handling.calculating import calc_surebets
from surebet.handling.matching import match_events
from surebet.handling.surebets import *
from surebet.parsing.bets import IdCondBet, CondBet

opposite_bets = {
    "o1": "o2",
    "o1x": "ox2",
}
opposite_bets.update({val: key for key, val in opposite_bets.items()})  # add reversed bets


def _get_reversed_event(event):
    event.team1, event.team2 = event.team2, event.team1

    for part in event.parts:
        part.o1, part.o2 = part.o2, part.o1
        part.o1x, part.ox2 = part.ox2, part.o1x

        for hand_idx, hand in enumerate(part.hand):
            if isinstance(part.hand[hand_idx], IdCondBet):
                part.hand[hand_idx] = IdCondBet(-hand.cond, hand.v2, hand.v1, hand.v2_id, hand.v1_id)
            else:  # TODO: remove when MaratBetting is to be merged
                part.hand[hand_idx] = CondBet(-hand.cond, hand.v2, hand.v1)

        part.ind_total1, part.ind_total2 = part.ind_total2, part.ind_total1

    return event


def _get_reversed_surebets(e_surebets):
    e_surebets.teams2 = (e_surebets.teams2[1], e_surebets.teams2[0])

    for part_surebets in e_surebets.parts:
        for surebet in part_surebets.surebets:
            w2_name = surebet.w2.name
            if w2_name.startswith("o"):  # if result bet
                opposite_bet = opposite_bets.get(w2_name, None)
                if opposite_bet:
                    surebet.w2.name = opposite_bet
            elif w2_name == "hand":
                surebet.w2.suffix = surebet.w1.suffix  # reverse equivalent for suffix's assign
            elif w2_name == "ind_total1" or w2_name == "ind_total2":
                surebet.w2.name = surebet.w1.name  # reverse equivalent for name's assign
    return e_surebets


def find_for_2_books(book1, book2):
    book_surebets = BookSurebets(book1.name, book2.name)

    for sport_name in book1.attrs_dict().keys():
        sport1, sport2 = getattr(book1, sport_name), getattr(book2, sport_name)

        with_draw = sport_name not in ("tennis", "volley")
        for event_pair in match_events(sport1, sport2):
            event1, event2 = event_pair.event1, event_pair.event2
            if event_pair.teams_reversed:
                event2 = _get_reversed_event(event2)

            e_surebets = EventSurebets((event1.team1, event1.team2), (event2.team1, event2.team2))

            part_bets2_map = {part_bets.part: part_bets for part_bets in event2.parts}
            for part_bets1 in event1.parts:
                part_num = part_bets1.part
                part_bets2 = part_bets2_map.get(part_num, None)
                if part_bets2:
                    part_surebets = calc_surebets(part_bets1, part_bets2, with_draw=with_draw)
                    if part_surebets:
                        e_surebets.parts.append(PartSurebets(part_surebets, part_num))

            if e_surebets.parts:
                if event_pair.teams_reversed:  # reverse second wagers in surebets
                    e_surebets = _get_reversed_surebets(e_surebets)

                sport = getattr(book_surebets, sport_name)
                sport.append(e_surebets)

    return book_surebets


def find_surebets(bookmakers):
    bookmakers.format()

    surebets = Surebets()
    for book_idx, book_surebets in enumerate(surebets.books_surebets):
        book1, book2 = getattr(bookmakers, book_surebets.book1), getattr(bookmakers, book_surebets.book2)
        surebets.books_surebets[book_idx] = find_for_2_books(book1, book2)

    return surebets
