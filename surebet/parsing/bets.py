from surebet.ancestors import *
from surebet.converting import format_spaces


class CustomBet(BetLevel):
    def __init__(self, factor: float, factor_id: int) -> None:
        self.factor = factor
        self.factor_id = factor_id

    def _not_empty(self):
        return self.factor


class CondBet(BetLevel):
    def __init__(self, cond, v1, v2) -> None:
        self.cond = cond
        self.v1 = v1  # Over/Hand1
        self.v2 = v2  # Under/Hand2

    def _not_empty(self):
        return self.v1 or self.v2


class CustomCondBet(CondBet):
    def __init__(self, cond, v1, v2, v1_id, v2_id) -> None:
        super().__init__(cond, v1, v2)
        self.v1_id = v1_id
        self.v2_id = v2_id


class PartBets(PartLevel):
    def __init__(self) -> None:
        super().__init__()
        self.o1, self.ox, self.o2, self.o1x, self.o12, self.ox2, = (0.0 for i in range(6))
        self.total, self.ind_total1, self.ind_total2, self.hand = ([] for i in range(4))


class FonbetPartBets(PartBets):
    def __init__(self) -> None:
        super().__init__()
        self.score = ""
        self.event_id = 0


class OlimpPartBets(PartBets):
    def __init__(self) -> None:
        super().__init__()
        self.sport_id = 0

    def _not_empty(self) -> bool:
        self._del_empty()

        skip_attrs = ["part", "sport_id"]
        attrs = [attr for attr, val in self.__dict__.items() if attr not in skip_attrs and val]
        return bool(attrs)


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
