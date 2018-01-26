from queue import Queue

from fuzzywuzzy import fuzz

from surebet.handling import MatchedEventPair

MIN_RATIO = 60


def match_events(events_arr1, events_arr2):
    first_events = Queue()
    for event in events_arr1:
        first_events.put(event)

    matched = {}
    while not first_events.empty():
        event1 = first_events.get()
        event2, max_ratio = _get_most_similar(events_arr2, event1, matched)

        if max_ratio > MIN_RATIO:
            if event2 not in matched:
                matched[event2] = event1
            else:
                first_events.put(matched[event2])
                del matched[event2]
                matched[event2] = event1

    for event2, event1 in matched.items():
        yield MatchedEventPair(event1, event2, _is_teams_reversed((event1, event2)))


def _get_most_similar(events_arr2, event1, matched):
    most_similar = None
    max_ratio = MIN_RATIO

    for event2 in events_arr2:
        cur_ratio = _calc_ratio((event1, event2))
        if cur_ratio > max_ratio and (event2 not in matched or cur_ratio > _calc_ratio((matched[event2], event2))):
            max_ratio = cur_ratio
            most_similar = event2
    return most_similar, max_ratio


def _calc_ratio(events):
    teams1, teams2 = _get_teams(events)
    return max(_get_ratio(teams1, teams2), _get_ratio(teams1, reversed(teams2)))


def _get_ratio(teams1, teams2):
    return fuzz.ratio(_join_teams(teams1), _join_teams(teams2))


def _join_teams(teams):
    return " ".join(teams)


def _get_teams(events):
    teams = []
    for event in events:
        teams.append(_format_teams(event))
    return teams


def _format_teams(event):
    return event.team1.lower(), event.team2.lower()


def _is_teams_reversed(events):
    teams1, teams2 = _get_teams(events)
    return _get_ratio(teams1, teams2) < _get_ratio(teams1, reversed(teams2))
