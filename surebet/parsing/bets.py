from surebet.ancestors import *
from surebet.converting import format_spaces


class CondBet(BetLevel):
    def __init__(self, cond, v1, v2) -> None:
        self.cond = cond
        self.v1 = v1  # Over/Hand1
        self.v2 = v2  # Under/Hand2

    def _not_empty(self):
        return self.v1 or self.v2


class PartBets(PartLevel):
    def __init__(self) -> None:
        super().__init__()
        self.o1, self.ox, self.o2, self.o1x, self.o12, self.ox2, = (0.0 for i in range(6))
        self.total, self.ind_total1, self.ind_total2, self.hand = ([] for i in range(4))


class Event(EventLevel):
    def __init__(self, team1, team2, parts) -> None:
        super().__init__(parts)
        self.team1 = team1
        self.team2 = team2

    def _format(self):
        self.team1 = format_spaces(self.team1)
        self.team2 = format_spaces(self.team2)


class Bookmaker(BookLevel):
    def __init__(self, name) -> None:
        super().__init__()
        self.name = name


class Bookmakers:
    def __init__(self) -> None:
        self.fonbet, self.olimp, self.marat = (Bookmaker(name) for name in ['fonbet', 'olimp', 'marat'])

    def format(self):
        for bookmaker in self.__dict__.values():
            bookmaker.format()


def exist_not_empty(el):
    return el and el._not_empty()
