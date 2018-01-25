from fuzzywuzzy import fuzz

from surebet.handling import MatchedEventPair

MATCH_RATIO = 70
ROUGH_RATIO = 95


def match_sports(sport1, sport2):
    matched_teams = set()
    matched_events = []
    undefined_pairs = []
    for event1 in sport1:
        for event2 in sport2:
            events = (event1, event2)
            events_teams = _get_teams(events)

            is_teams_reversed = _match_events(*events)
            if is_teams_reversed is not None:
                matched_pair = MatchedEventPair(*events, is_teams_reversed)

                used_teams = _get_used_teams(events_teams, matched_teams)
                if used_teams:
                    undefined_pairs.append(matched_pair)

                    used_pair = _pop_used_pair(matched_events, used_teams)
                    if used_pair:
                        undefined_pairs.append(used_pair)
                    continue

                matched_teams.update(events_teams)
                matched_events.append(matched_pair)

    if undefined_pairs:
        print("Undefined pairs: {}".format(len(undefined_pairs)))
        matched_events.extend(_match_undefined_pairs(undefined_pairs))

    return matched_events


def _join_teams(teams):
    return " ".join(teams)


def _match_events(event1, event2, match_ratio=MATCH_RATIO):
    is_teams_reversed = None

    teams1 = _format_teams(event1)
    teams2 = _format_teams(event2)
    if _is_equal(_join_teams(teams1), _join_teams(teams2), match_ratio):
        is_teams_reversed = False
    elif _is_equal(_join_teams(teams1), _join_teams(reversed(teams2)), match_ratio):
        is_teams_reversed = True

    return is_teams_reversed


def _format_teams(event):
    return event.team1.lower(), event.team2.lower()


def _is_equal(str1, str2, match_ratio):
    return fuzz.ratio(str1, str2) > match_ratio


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


def _pop_used_pair(matched_events, used_teams):
    for pair_idx, matched_pair in enumerate(matched_events):
        for event in (matched_pair.event1, matched_pair.event2):
            if (event.team1, event.team2) == (used_teams[0], used_teams[1]):
                return matched_events.pop(pair_idx)
    return None


def _match_undefined_pairs(undefined_pairs):
    matched_events = []
    for pair in undefined_pairs:
        events = (pair.event1, pair.event2)

        is_teams_reversed = _match_events(*events, match_ratio=ROUGH_RATIO)
        if is_teams_reversed is not None:
            matched_events.append(MatchedEventPair(*events, is_teams_reversed))
    return matched_events
