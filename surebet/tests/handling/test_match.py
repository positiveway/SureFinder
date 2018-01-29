import pickle

from os import path

from surebet import *
from surebet.handling import *
from surebet.handling.matching import match_events
from surebet.tests.handling import *

resource_dir = path.join(package_dir, "matching")

allowable_ratio = 0.9


def test_intersection():
    filename = path.join(resource_dir, "intersection.json")
    with open(filename) as file:
        known_res = json.load(file)

    filename = path.join(resource_dir, "intersection.pkl")
    with open(filename, "rb") as file:
        bookmakers = pickle.load(file)

    matched_events = get_matched_events(bookmakers)

    if calc_intersection_len(matched_events, known_res) / len(known_res) < allowable_ratio:
        raise HandlingException("too few events were matched")

    logging.info("PASS: intersection")


def get_matched_events(bookmakers):
    matched_events = []
    for book1_name, book2_name in combinations(book_names, 2):
        book1, book2 = getattr(bookmakers, book1_name), getattr(bookmakers, book2_name)
        for sport_name in book1.attrs_dict().keys():
            sport1, sport2 = getattr(book1, sport_name), getattr(book2, sport_name)

            for event_pair in match_events(sport1, sport2):
                matched_events.append(event_pair)
    return matched_events


def calc_intersection_len(matched_events, known_res):
    intersection_len = 0
    for matched_pair in matched_events:
        for known_pair in known_res:
            is_equal = True
            for cur_event in ("event1", "event2"):
                matched_pair_event = getattr(matched_pair, cur_event)
                known_pair_event = known_pair[cur_event]
                if (matched_pair_event.team1, matched_pair_event.team2) != \
                        (known_pair_event["team1"], known_pair_event["team2"]):
                    is_equal = False
                    break
            if matched_pair.teams_reversed == known_pair["teams_reversed"] and is_equal:
                intersection_len += 1
                break
    return intersection_len


def test_sample():
    for sample_num in range(3):
        filename = path.join(resource_dir, "sample{}.pkl".format(sample_num))
        with open(filename, "rb") as file:
            bookmakers = pickle.load(file)

        get_matched_events(bookmakers)

        logging.info('PASS: sample{}'.format(sample_num))

    logging.info("PASS: sample")
