import re
import requests
import json
from surebet.loading import check_status, log_loaded

name = "marat"

url = "https://www.marathonbet.co.uk/en/live"
live_elem = "#container_AVAILABLE > div"

sports = ["45356", "26418", "43658", "22723", "23690"]
sport_names = ["Basketball", "Football", "Ice Hockey", "Tennis", "Volleyball"]

details_url = "https://www.marathonbet.co.uk/en/livemarkets.htm?treeId={}"


def load_events():
    r = requests.get(url)
    check_status(name, r.status_code)

    site_html = r.text
    res = re.search(r"reactData = ({.*});", site_html)
    raw_sport_tree = json.loads(res.group(1))["liveMenuEvents"]["childs"]

    sport_tree = process_sport_tree(raw_sport_tree)

    events = []
    add_info = {}
    for sport in sport_tree:
        if sport["name"] == "Tennis" or sport["name"] == "Volleyball":
            html = get_add_info(sport["id"])
            if html:
                add_info[sport["name"]] = html
        for event in sport["events"]:
            event_details = get_event_details(event["id"])
            if event_details:
                events.append(event_details)

    log_loaded(name)
    return {"events": events, "add_info": add_info, "sport_tree": sport_tree}


def process_sport_tree(raw_sport_tree):
    sport_tree = []
    for sport in raw_sport_tree:
        if sport["label"] not in sport_names:
            continue

        new_sport = {"name": sport["label"], "id": sport["uid"], "events": []}
        for category in sport["childs"]:
            for event in category["childs"]:
                new_event = {"name": event["label"], "id": event["uid"]}
                new_sport["events"].append(new_event)
        sport_tree.append(new_sport)
    return sport_tree


def get_event_details(event_id):
    req_url = details_url.format(event_id)

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    r = requests.post(req_url, headers=headers)
    if r.status_code == 204:
        return None
    check_status(name, r.status_code)

    return r.json()["ADDITIONAL_MARKETS"]


def get_add_info(sport_id):
    req_url = url + "/{}".format(sport_id)

    r = requests.get(req_url)
    check_status(name, r.status_code)

    return r.text
