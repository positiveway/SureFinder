from itertools import combinations

from surebet.handling.surebets import Surebets

book_names = ["fonbet", "marat", "olimp"]


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
