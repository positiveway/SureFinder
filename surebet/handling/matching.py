from fuzzywuzzy import fuzz

from surebet.handling import MatchedEventPair

MATCH_RATIO = 80


def match_sports(sport1, sport2):
    for event1 in sport1:
        for event2 in sport2:
            reversed_teams = _match_events(event1, event2)
            if reversed_teams is not None:
                yield MatchedEventPair(event1, event2, reversed_teams)


def _join_teams(team1, team2):
    return " ".join((team1, team2))


def _match_events(event1, event2):
    reversed_teams = None

    teams1 = (event1.team1, event1.team2)
    teams2 = (event2.team1, event2.team2)
    if _is_equal(_join_teams(*teams1), _join_teams(*teams2)):
        reversed_teams = False
    elif _is_equal(_join_teams(*teams1), _join_teams(*reversed(teams2))):
        reversed_teams = True

    return reversed_teams


def _is_equal(str1, str2):
    return fuzz.ratio(str1, str2) > MATCH_RATIO
