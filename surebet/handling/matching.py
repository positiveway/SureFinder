from fuzzywuzzy import fuzz

from surebet.handling import MatchedEventPair

MATCH_RATIO = 70
ROUGH_RATIO = 95


def match_sports(sport1, sport2):
    matched_teams = set()
    matched_events = []

    for event1 in sport1:
        for event2 in sport2:
            events = (event1, event2)
            events_teams = _get_teams(events)

            is_teams_reversed = _match_events(*events)
            if is_teams_reversed is not None:
                matched_pair = MatchedEventPair(*events, is_teams_reversed)

                used_teams = _get_used_teams(events_teams, matched_teams)
                if used_teams:
                    _del_used_pair(matched_events, used_teams)
                    continue

                matched_teams.update(events_teams)
                matched_events.append(matched_pair)

    return matched_events


def _join_teams(team1, team2):
    return " ".join((team1, team2))


def _match_events(event1, event2):
    is_teams_reversed = None

    teams1 = _format_teams(event1)
    teams2 = _format_teams(event2)
    if _is_equal(_join_teams(*teams1), _join_teams(*teams2)):
        is_teams_reversed = False
    elif _is_equal(_join_teams(*teams1), _join_teams(*reversed(teams2))):
        is_teams_reversed = True

    return is_teams_reversed


def _format_teams(event):
    return event.team1.lower(), event.team2.lower()


def _is_equal(str1, str2, match_ration=MATCH_RATIO):
    return fuzz.ratio(str1, str2) > match_ration


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
            if (event.team1, event.team2) == (used_teams[0], used_teams[1]):
                del matched_events[pair_idx]
                return
