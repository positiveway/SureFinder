class BetLevel:
    """Represent level of bet. Could contain info about bet or surebet."""
    def _not_empty(self):
        pass


class PartLevel:
    """
    Represent level of event's part. Each part of event has number
    (e.g.: 1st half for Soccer - number equals 1).
    """
    def __init__(self) -> None:
        # if self.part equals 0, it means that PartLevel describes whole match, not just part of it
        self.part = 0

    def _not_empty(self):
        """
        Delete empty bets or surebets for current part and check
        if there are remain at least one non-empty attribute.
        """
        self._del_empty()

        attrs = [attr for attr, val in self.__dict__.items() if attr != 'part' and val]
        return bool(attrs)

    def _del_empty(self):
        bets = {attr: val for (attr, val) in self.__dict__.items() if isinstance(val, list)}
        for attr, val in bets.items():
            new_val = [bet for bet in val if _exist_not_empty(bet)]
            setattr(self, attr, new_val)


class EventLevel:
    """
    Represent level of event. Each event has parts
    (e.g.: 1st half for Soccer or 2nd period for Hockey).
    """
    def __init__(self, parts) -> None:
        """
        :param parts: list of parts(class PartLevel) for event
        """
        self.parts = parts

    def _not_empty(self):
        """Delete empty parts of event and check if attribute parts is not empty."""
        self._del_empty()

        return bool(self.parts)

    def _del_empty(self):
        self.parts = [part for part in self.parts if _exist_not_empty(part)]

    def _format(self):
        pass


class BookLevel:
    """Represent level of bookmaker, on which bookmaker has 5 types of sports."""
    def __init__(self) -> None:
        # lists of objects of class EventLevel for certain sports
        self.soccer, self.tennis, self.hockey, self.basket, self.volley = ([] for i in range(5))

    def attrs_dict(self):
        """Return attribute name and value for each type of sport."""
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
        """Format events and delete empty events for each sport list."""
        self._del_empty()
        self._format()


def _exist_not_empty(el):
    return el and el._not_empty()
