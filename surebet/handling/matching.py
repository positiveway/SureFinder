from fuzzywuzzy import fuzz

from surebet.handling import MatchedEventPair

MATCH_RATIO = 80


def match_sports(sport1, sport2):
    matched_events = []
    for event1 in sport1:
        for event2 in sport2:
            reversed_teams = match_events(event1, event2)
            if reversed_teams is not None:
                matched_events.append(MatchedEventPair(event1, event2, reversed_teams))

    return matched_events


def join_teams(team1, team2):
    return " ".join((team1, team2))


def match_events(event1, event2):
    reversed_teams = None

    teams1 = (event1.team1, event1.team2)
    teams2 = (event2.team1, event2.team2)
    if is_equal(join_teams(*teams1), join_teams(*teams2)):
        reversed_teams = False
    elif is_equal(join_teams(*teams1), join_teams(*reversed(teams2))):
        reversed_teams = True

    return reversed_teams


def is_equal(str1, str2):
    return fuzz.ratio(str1, str2) > MATCH_RATIO
