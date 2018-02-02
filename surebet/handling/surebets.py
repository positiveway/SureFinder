from itertools import combinations

book_names = ["fonbet", "marat", "olimp"]

HOLDING_LIMIT = 15


class Wager:
    def __init__(self, name: str, factor: float):
        self.name = name
        self.factor = factor

    def __eq__(self, other):
        return self.name == other.name


class CondWager(Wager):
    def __init__(self, name: str, factor: float, suffix: str, cond: float):
        """
        :param suffix: suffix for wager (for instance: Hand1, "1" - suffix; TotalU, "U" - suffix)
        :param cond: condition for wager (for instance: Hand1(-1.5), "-1.5" - cond; TotalU(2.5), "2.5" - cond)
        """
        super().__init__(name, factor)
        self.cond = cond
        self.suffix = suffix

    def __eq__(self, other):
        return super().__eq__(other) and self.suffix == other.suffix and self.cond == other.cond


class Surebet:
    def __init__(self, w1: Wager, w2: Wager, profit: float = None):
        """
        :param w1, w2: first and second wagers of surebet
        :param profit: surebet's profit
        """
        self.w1 = w1
        self.w2 = w2
        self.profit = profit

    def __eq__(self, other):
        return self.w1 == other.w1 and self.w2 == other.w2


class MarkedSurebet(Surebet):
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


class PartSurebets:
    def __init__(self, surebets: list, part: int):
        """
        :param surebets: list of surebets (class Surebet/MarkedSurebet)
        :param part: number of event's part
        """
        self.surebets = surebets
        self.part = part

    def __eq__(self, other):
        return self.part == other.part


class EventSurebets:
    def __init__(self, teams1: list, teams2: list):
        """
        :params teams1, teams2: lists of teams for first and second event
        :param parts: list of surebets for certain parts of event (class PartSurebets)
        """
        self.teams1, self.teams2 = teams1, teams2
        self.parts = []

    def __eq__(self, other):
        return self.teams1 == other.teams1 and self.teams2 == other.teams2


class BookSurebets:
    def __init__(self, book1: str, book2: str):
        """
        :param book1, book2: bookmakers names
        :params soccer, tennis, hockey, basket, volley: lists of surebets for certain sports, each consists of surebets
            for certain events (EventSurebets)
        """
        self.book1, self.book2 = book1, book2
        self.soccer, self.tennis, self.hockey, self.basket, self.volley = ([] for i in range(5))

    def attrs_dict(self) -> dict:
        return {attr: val for attr, val in self.__dict__.items() if isinstance(val, list)}

    def __eq__(self, other):
        return self.book1 == other.book1 and self.book2 == other.book2


class Surebets:
    def __init__(self):
        """
        :param books_surebets: list of surebets for every pair of bookmakers (BookSurebets)
        """
        self.books_surebets = []
        for book1_name, book2_name in combinations(book_names, 2):
            self.books_surebets.append(BookSurebets(book1_name, book2_name))
