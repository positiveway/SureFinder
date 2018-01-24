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


class EventSurebets:
    def __init__(self, teams1, teams2):
        self.teams1, self.teams2 = teams1, teams2
        self.parts = []


class Surebets:
    def __init__(self, book1, book2):
        self.book1, self.book2 = book1, book2
        self.soccer, self.tennis, self.hockey, self.basket, self.volley = ([] for i in range(5))


def generate_all_surebets():
    all_surebets = []
    for book1_name, book2_name in combinations(book_names, 2):
        all_surebets.append(Surebets(book1_name, book2_name))
    return all_surebets


class HandlingException(Exception):
    pass


class MatchedEventPair:
    def __init__(self, event1, event2, teams_reversed):
        self.event1 = event1
        self.event2 = event2
        # defines if event2's teams have reversed order accordingly to event1
        self.teams_reversed = teams_reversed
