from itertools import combinations

book_names = ["fonbet", "marat", "olimp"]

HOLDING_LIMIT = 15


class Wager:
    def __init__(self, name, factor):
        self.name = name
        self.factor = factor

    def __eq__(self, other):
        return self.name == other.name


class CondWager(Wager):
    def __init__(self, name, factor, suffix, cond):
        super().__init__(name, factor)
        self.cond = cond
        self.suffix = suffix

    def __eq__(self, other):
        return super().__eq__(other) and self.suffix == other.suffix and self.cond == other.cond


class Surebet:
    def __init__(self, w1, w2, profit=None):
        self.w1 = w1
        self.w2 = w2
        self.profit = profit

    def __eq__(self, other):
        return self.w1 == other.w1 and self.w2 == other.w2


class MarkedSurebet(Surebet):
    def __init__(self, w1, w2, profit=None):
        super().__init__(w1, w2, profit)
        self.mark = HOLDING_LIMIT

    def restore_mark(self):
        self.mark = HOLDING_LIMIT

    def dec_mark(self):
        self.mark -= 1

    def is_mark_empty(self):
        return self.mark == 0


class PartSurebets:
    def __init__(self, surebets, part):
        self.surebets = surebets
        self.part = part

    def __eq__(self, other):
        return self.part == other.part


class EventSurebets:
    def __init__(self, teams1, teams2):
        self.teams1, self.teams2 = teams1, teams2
        self.parts = []

    def __eq__(self, other):
        attrs = ('teams1', 'teams2')
        checks = [self._teams_equal(getattr(self, attr), getattr(other, attr)) for attr in attrs]
        return all(checks)

    @staticmethod
    def _teams_equal(teams1, teams2) -> bool:
        return tuple(teams1) == tuple(teams2)


class BookSurebets:
    def __init__(self, book1, book2):
        self.book1, self.book2 = book1, book2
        self.soccer, self.tennis, self.hockey, self.basket, self.volley = ([] for i in range(5))

    def attrs_dict(self):
        return {attr: val for attr, val in self.__dict__.items() if isinstance(val, list)}

    def __eq__(self, other):
        return self.book1 == other.book1 and self.book2 == other.book2


class Surebets:
    def __init__(self):
        self.books_surebets = []
        for book1_name, book2_name in combinations(book_names, 2):
            self.books_surebets.append(BookSurebets(book1_name, book2_name))
