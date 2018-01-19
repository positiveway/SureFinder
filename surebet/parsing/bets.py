from surebet.converting import format_spaces


class CondBet:
    def __init__(self, cond, v1, v2) -> None:
        self.cond = cond
        self.v1 = v1  # Over/Hand1
        self.v2 = v2  # Under/Hand2

    def _not_empty(self):
        return self.v1 or self.v2


class PartBets:
    def __init__(self) -> None:
        self.part = 0
        self.o1, self.ox, self.o2, self.o1x, self.o12, self.ox2, = (0.0 for i in range(6))
        self.total, self.ind_total1, self.ind_total2, self.hand = ([] for i in range(4))

    def _not_empty(self):
        self._del_empty()

        attrs = [attr for attr, val in self.__dict__.items() if attr != 'part' and val]
        return bool(attrs)

    def _del_empty(self):
        cond_bets = {attr: val for (attr, val) in self.__dict__.items() if isinstance(val, list)}
        for attr, val in cond_bets.items():
            new_val = [cond_bet for cond_bet in val if exist_not_empty(cond_bet)]
            setattr(self, attr, new_val)


class Event:
    def __init__(self, team1, team2, parts) -> None:
        self.team1 = team1
        self.team2 = team2
        self.parts = parts

    def _not_empty(self):
        self._del_empty()

        return bool(self.parts)

    def _del_empty(self):
        self.parts = [part_bets for part_bets in self.parts if exist_not_empty(part_bets)]

    def _format(self):
        self.team1 = format_spaces(self.team1)
        self.team2 = format_spaces(self.team2)


class Bookmaker:
    def __init__(self, name) -> None:
        self.name = name
        self.soccer, self.tennis, self.hockey, self.basket, self.volley = ([] for i in range(5))

    def _del_empty(self):
        items = [(attr, val) for attr, val in self.__dict__.items() if attr != "name"]
        for attr, val in items:
            new_val = [event for event in val if exist_not_empty(event)]
            setattr(self, attr, new_val)

    def _format(self):
        values = [val for attr, val in self.__dict__.items() if attr != "name"]
        for val in values:
            for event in val:
                event._format()

    def format(self):
        self._del_empty()
        self._format()


class Bookmakers:
    def __init__(self) -> None:
        self.fonbet, self.olimp, self.marat = (Bookmaker(name) for name in ['fonbet', 'olimp', 'marat'])

    def format(self):
        for bookmaker in self.__dict__.values():
            bookmaker.format()


def exist_not_empty(el):
    return el and el._not_empty()
