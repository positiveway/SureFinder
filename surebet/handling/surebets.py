from itertools import combinations

book_names = ["fonbet", "marat", "olimp"]


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
        return self.teams1 == other.teams1 and self.teams2 == other.teams2


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
