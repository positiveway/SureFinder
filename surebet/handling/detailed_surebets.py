from functools import cmp_to_key
from surebet.handling.surebets import *

PROFIT_LOW_LIM = 1
PROFIT_UP_LIM = 10

LIFETIME_LOW_LIM = 15


class DetailedSurebet:
    """
    Contain all information about surebet: bookmakers between which surebet is appeared,
    teams for first and second event, part of event and wagers, profit, life time of surebet
    """

    def __init__(self, books: BookSurebets, sport: str, events: EventSurebets, part: PartSurebets,
                 surebet: TimedSurebet):
        """
        :param books: bookmakers between which surebet is appeared
        :param sport: name of sport
        :param events: events between which surebet is appeared
        :param part: common part of events
        """
        self.book1, self.book2 = books.book1, books.book2
        self.sport = sport
        self.teams1, self.teams2 = events.teams1, events.teams2
        self.part = part.part
        self.w1, self.w2 = surebet.w1, surebet.w2
        self.profit = surebet.profit
        self.life_time = surebet.get_lifetime()

    def __str__(self):
        event_name1 = " vs ".join(self.teams1)
        event_name2 = " vs ".join(self.teams2)
        str_form = "profit: {profit:<8} | {sport:<6} | {book1:<6} | {ev_name1:<60} | part #{part} | {w1}\n".format(
            profit=self.profit, book1=self.book1, sport=self.sport, ev_name1=event_name1, part=self.part,
            w1=self.w1)
        str_form += "lifetime: {time:<6} | {sport:<6} | {book2:<6} | {ev_name2:<60} | part #{part} | {w2}\n".format(
            time=self.life_time, book2=self.book2, sport=self.sport, ev_name2=event_name2, part=self.part,
            w2=self.w2)
        return str_form


def convert_to_detailed(surebets: Surebets):
    """Convert surebets to list of DetailedSurebet, filter that list and sort"""
    detailed_surebets = _convert_to_detailed(surebets)

    detailed_surebets = list(_filter(detailed_surebets))

    detailed_surebets.sort(key=cmp_to_key(_detailed_cmp), reverse=True)

    return detailed_surebets


def _filter(detailed_surebets):
    """Filter detailed_surebets by profit's lower and upper limits and by life_time's lower limit"""
    return filter(lambda item: PROFIT_LOW_LIM <= item.profit <= PROFIT_UP_LIM and LIFETIME_LOW_LIM <= item.life_time,
                  detailed_surebets)


def _convert_to_detailed(surebets: Surebets):
    """Construct objects of class DetailedSurebet and put them in list detailed_surebets"""
    detailed_surebets = []
    for book in surebets.books_surebets:
        for sport_name, sport in book.attrs_dict().items():
            for event in sport:
                for part in event.parts:
                    for surebet in part.surebets:
                        detailed_surebets.append(DetailedSurebet(book, sport_name, event, part, surebet))
    return detailed_surebets


def _detailed_cmp(first: DetailedSurebet, second: DetailedSurebet):
    """Custom comparator to sort detailed_surebets firstly by profit casted to int and secondly by life_time"""
    first_profit, second_profit = int(first.profit), int(second.profit)
    if first_profit < second_profit:
        return -1
    elif first_profit == second_profit:
        return first.life_time - second.life_time
    else:
        return 1
