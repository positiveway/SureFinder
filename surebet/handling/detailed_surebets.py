from functools import cmp_to_key
from surebet.handling.surebets import *

MIN_PROFIT = 2.5
MAX_PROFIT = 10

MIN_LIFETIME = 5


class DetailedSurebet:
    """
    Contain all information about surebet: bookmakers between which surebet is occurred,
    teams for first and second event, part of event and wagers, profit, lifetime of surebet
    """

    def __init__(self, books: BookSurebets, sport: str, events: EventSurebets, part: PartSurebets,
                 surebet: TimedSurebet) -> None:
        """
        :param books: bookmakers between which surebet is occurred
        :param sport: name of sport
        :param events: events between which surebet is occurred
        :param part: common part of events
        """
        self.book1, self.book2 = books.book1, books.book2
        self.sport = sport
        self.teams1, self.teams2 = events.teams1, events.teams2
        self.part = part.part
        self.w1, self.w2 = surebet.w1, surebet.w2
        self.profit = surebet.profit
        self.lifetime = surebet.get_lifetime()

    def __str__(self):
        teams_sep = " vs "
        event_name1 = teams_sep.join(self.teams1)
        event_name2 = teams_sep.join(self.teams2)

        common_pattern = "{book:<6} | {ev_name:<60} | {wager}\n"

        str_form = "profit: {profit:<5} | lifetime: {time:<6} | {sport:<6} | part: {part}\n".format(
            profit=self.profit, time=self.lifetime, sport=self.sport, part=self.part)

        second_line = common_pattern.format(book=self.book1, ev_name=event_name1, wager=self.w1)
        str_form += second_line
        str_form += common_pattern.format(book=self.book2, ev_name=event_name2, wager=self.w2)
        str_form += "-" * len(second_line)

        return str_form


def convert_to_detailed(surebets: Surebets) -> list:
    """Convert surebets to list of DetailedSurebet, filter that list and sort"""
    detailed_surebets = _convert_to_detailed(surebets)

    detailed_surebets = _filter(detailed_surebets)

    _sort_detailed(detailed_surebets)

    return detailed_surebets


def _filter(detailed_surebets: list) -> list:
    """Filter detailed_surebets by profit's lower and upper limits and by lifetime's lower limit"""

    def predicate(item) -> bool:
        return MIN_PROFIT <= item.profit <= MAX_PROFIT and item.lifetime >= MIN_LIFETIME

    return list(filter(predicate, detailed_surebets))


def _convert_to_detailed(surebets: Surebets) -> list:
    """Construct objects of class DetailedSurebet and put them in list detailed_surebets"""
    detailed_surebets = []
    for book in surebets.books_surebets:
        for sport_name, sport in book.attrs_dict().items():
            for event in sport:
                for part in event.parts:
                    for surebet in part.surebets:
                        detailed_surebets.append(DetailedSurebet(book, sport_name, event, part, surebet))
    return detailed_surebets


def _sort_detailed(detailed_surebets: list) -> None:
    detailed_surebets.sort(key=cmp_to_key(_detailed_cmp), reverse=True)


def _detailed_cmp(first: DetailedSurebet, second: DetailedSurebet):
    """Custom comparator to sort detailed_surebets firstly by profit casted to int and secondly by lifetime"""
    first_profit, second_profit = int(first.profit), int(second.profit)
    if first_profit != second_profit:
        return first_profit - second_profit
    else:
        return first.lifetime - second.lifetime
