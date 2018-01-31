class HandlingException(Exception):
    pass


class MatchedEventPair:
    def __init__(self, event1, event2, teams_reversed):
        self.event1 = event1
        self.event2 = event2
        # defines if event2's teams have reversed order accordingly to event1
        self.teams_reversed = teams_reversed
