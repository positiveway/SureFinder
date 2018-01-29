from queue import Queue

from fuzzywuzzy import fuzz

from surebet.handling import MatchedEventPair

MIN_RATIO = 60


def match_events(events1, events2):
    first_events = Queue()
    for event in events1:
        first_events.put(event)
    matched = {}
    while not first_events.empty():
        event1 = first_events.get()
        max_ratio = MIN_RATIO
        found_event = None

        for event2 in events2:
            cur_ratio = calc_ratio((event1, event2))
            if cur_ratio > max_ratio:
                if event2 not in matched or cur_ratio > calc_ratio((matched[event2], event2)):
                    max_ratio = cur_ratio
                    found_event = event2

        if max_ratio == MIN_RATIO:
            continue

        if found_event not in matched:
            matched[found_event] = event1
        else:
            first_events.put(matched[found_event])
            del matched[found_event]
            matched[found_event] = event1

    for event2, event1 in matched.items():
        yield MatchedEventPair(event1, event2, is_teams_reversed((event1, event2)))


def calc_ratio(events):
    teams1, teams2 = get_teams(events)
    return max(_calc_ratio(teams1, teams2), _calc_ratio(teams1, reversed(teams2)))


def _calc_ratio(teams1, teams2):
    return fuzz.ratio(join_teams(teams1), join_teams(teams2))


def join_teams(teams):
    return " ".join(teams)


def get_teams(events):
    teams = []
    for event in events:
        teams.append(format_teams(event))
    return teams


def format_teams(event):
    return event.team1.lower(), event.team2.lower()


def is_teams_reversed(events):
    teams1, teams2 = get_teams(events)
    return _calc_ratio(teams1, teams2) < _calc_ratio(teams1, reversed(teams2))
