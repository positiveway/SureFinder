class BetLevel:
    def _not_empty(self):
        pass


class PartLevel:
    def __init__(self) -> None:
        self.part = 0

    def _not_empty(self):
        self._del_empty()

        attrs = [attr for attr, val in self.__dict__.items() if attr != 'part' and val]
        return bool(attrs)

    def _del_empty(self):
        bets = {attr: val for (attr, val) in self.__dict__.items() if isinstance(val, list)}
        for attr, val in bets.items():
            new_val = [bet for bet in val if _exist_not_empty(bet)]
            setattr(self, attr, new_val)


class EventLevel:
    def __init__(self, parts) -> None:
        self.parts = parts

    def _not_empty(self):
        self._del_empty()

        return bool(self.parts)

    def _del_empty(self):
        self.parts = [part for part in self.parts if _exist_not_empty(part)]

    def _format(self):
        pass


class BookLevel:
    def __init__(self) -> None:
        self.soccer, self.tennis, self.hockey, self.basket, self.volley = ([] for i in range(5))

    def attrs_dict(self):
        return {attr: val for attr, val in self.__dict__.items() if isinstance(val, list)}

    def _del_empty(self):
        for attr, val in self.attrs_dict().items():
            new_val = [event for event in val if _exist_not_empty(event)]
            setattr(self, attr, new_val)

    def _format(self):
        for sport in self.attrs_dict().values():
            for event in sport:
                event._format()

    def format(self):
        self._del_empty()
        self._format()


def _exist_not_empty(el):
    return el and el._not_empty()
