from fuzzywuzzy import fuzz

from surebet.handling import MatchedEventPair

MATCH_RATIO = 70


def match_sports(sport1, sport2):
    matched_teams = set()
    matched_events = []

    for event1 in sport1:
        for event2 in sport2:
            events = (event1, event2)
            events_teams = _get_teams(events)

            reversed_teams = _match_events(*events)
            if reversed_teams is not None:
                used_teams = _get_used_teams(events_teams, matched_teams)
                if used_teams:
                    _del_used_pair(matched_events, used_teams)
                    continue

                matched_teams.update(events_teams)
                matched_events.append(MatchedEventPair(*events, reversed_teams))

    return matched_events


def _join_teams(team1, team2):
    return " ".join((team1, team2))


def _match_events(event1, event2):
    reversed_teams = None

    teams1 = (event1.team1.lower(), event1.team2.lower())
    teams2 = (event2.team1.lower(), event2.team2.lower())
    if _is_equal(_join_teams(*teams1), _join_teams(*teams2)):
        reversed_teams = False
    elif _is_equal(_join_teams(*teams1), _join_teams(*reversed(teams2))):
        reversed_teams = True

    return reversed_teams


def _is_equal(str1, str2):
    return fuzz.ratio(str1, str2) > MATCH_RATIO


def _get_teams(events):
    teams = []
    for event in events:
        teams.append((event.team1, event.team2))
    return teams


def _get_used_teams(events_teams, matched_teams):
    for teams in events_teams:
        if teams in matched_teams:
            return teams
    return None


def _del_used_pair(matched_events, used_teams):
    for pair_idx, matched_pair in enumerate(matched_events):
        for event in (matched_pair.event1, matched_pair.event2):
            if event.team1 == used_teams[0] and event.team2 == used_teams[1]:
                del matched_events[pair_idx]
                return
