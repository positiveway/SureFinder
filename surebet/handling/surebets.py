from collections import Iterable
from itertools import combinations

from surebet.ancestors import *

book_names = ["fonbet", "marat", "olimp"]

HOLDING_LIMIT = 15


class Wager:
    """Base info about bet."""

    def __init__(self, name: str, factor: float):
        """
        :param name: name of bet (for instance: O1X, O12)
        :param factor: coefficient of bet
        """
        self.name = name
        self.factor = factor

    def _not_empty(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name


class CondWager(Wager):
    """Class for bets with condition, that is Handicap or Total."""

    def __init__(self, name: str, factor: float, suffix: str, cond: float):
        """
        :param suffix: suffix for wager (e.g.: Hand1, "1" - suffix; TotalU, "U" - suffix)
        :param cond: condition for wager (e.g.: Hand1(-1.5), "-1.5" - cond; TotalU(2.5), "2.5" - cond)
        """
        super().__init__(name, factor)
        self.cond = cond
        self.suffix = suffix

    def _not_empty(self):
        return super()._not_empty() and self.cond and self.suffix

    def __eq__(self, other):
        return super().__eq__(other) and self.suffix == other.suffix and self.cond == other.cond


class Surebet(BetLevel):
    """Contains 2 wagers and profit between them."""

    def __init__(self, w1: Wager, w2: Wager, profit: float = None):
        """
        :param w1, w2: first and second wagers of surebet
        :param profit: surebet's profit
        """
        self.w1 = w1
        self.w2 = w2
        self.profit = profit

    def _not_empty(self):
        return self.w1._not_empty() and self.w2._not_empty()

    def __eq__(self, other):
        return self.w1 == other.w1 and self.w2 == other.w2


class MarkedSurebet(Surebet):
    """
    Specialized class for handling "Positive" buffer. Contains mark
    designating how many loadings left to remove it.
    After surebet's mark decreased from HOLDING_LIMIT to 0,
    surebet can be considered as gone, that is
    it's disappeared from positivebet pool.
    """

    def __init__(self, w1: Wager, w2: Wager, profit: float = None):
        """
        :param mark: indicates whether surebet is actual or not
        """
        super().__init__(w1, w2, profit)
        self.mark = HOLDING_LIMIT

    def restore_mark(self):
        self.mark = HOLDING_LIMIT

    def dec_mark(self):
        self.mark -= 1

    def is_mark_empty(self) -> bool:
        return self.mark == 0


class PartSurebets(PartLevel):
    """Contains surebets for specific part of event. Defines number of part."""

    def __init__(self, surebets: list, part: int):
        """
        :param surebets: list of surebets (class Surebet/MarkedSurebet)
        :param part: number of event's part
        """
        super().__init__()
        self.surebets = surebets
        self.part = part

    def __eq__(self, other):
        return self.part == other.part


class EventSurebets(EventLevel):
    """
    Surebets appear between two events. This pair of events has common parts
    (e.g: period for hockey, set for tennis etc.)
    So this class contains surebets for each common part of event's pair.
    """

    def __init__(self, teams1: Iterable, teams2: Iterable):
        """
        :params teams1, teams2: lists of teams for first and second event
        :param parts: list of surebets for certain parts of event's pair (class PartSurebets)
        """
        super().__init__([])
        self.teams1, self.teams2 = teams1, teams2

    def __eq__(self, other):
        attrs = ('teams1', 'teams2')
        checks = [self._teams_equal(getattr(self, attr), getattr(other, attr)) for attr in attrs]
        return all(checks)

    @staticmethod
    def _teams_equal(teams1, teams2) -> bool:
        return tuple(teams1) == tuple(teams2)


class BookSurebets(BookLevel):
    """Surebets for 2 bookmakers (e.g Olimp, Fonbet)."""

    def __init__(self, book1: str, book2: str):
        """
        :param book1, book2: bookmakers names
        :params soccer, tennis, hockey, basket, volley: lists of surebets for certain sports, each consists of surebets
            for certain events (EventSurebets)
        """
        super().__init__()
        self.book1, self.book2 = book1, book2

    def __eq__(self, other):
        return self.book1 == other.book1 and self.book2 == other.book2


class Surebets:
    """Pairs of BookSurebets in alphabetical order."""

    def __init__(self):
        """
        :param books_surebets: list of surebets for every pair of bookmakers (BookSurebets)
        """
        self.books_surebets = []
        for book1_name, book2_name in combinations(book_names, 2):
            self.books_surebets.append(BookSurebets(book1_name, book2_name))

    def format(self):
        for book_surebets in self.books_surebets:
            book_surebets.format()
