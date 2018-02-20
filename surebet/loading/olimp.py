import asyncio

import aiohttp
import requests
from hashlib import md5

from surebet.loading import check_status, log_loaded_events
from surebet.loading.async import async_post

name = "olimp"

base_url = "http://191.101.165.203:10600/api/{}"

secret_key = "b2c59ba4-7702-4b12-bef5-0908391851d9"

base_payload = {
    "platforma": "ANDROID1",
    "lang_id": "2",
    "time_shift": "0",
}

live_payload = base_payload.copy()
live_payload["live"] = "1"

base_headers = {
    "User-Agent": "okhttp/3.8.0",
}

sports_by_id = {
    1: "soccer",
    5: "basket",
    2: "hockey",
    3: "tennis",
    10: "volley",
}


def get_xtoken(payload):
    sorted_values = [str(payload[key]) for key in sorted(payload.keys())]
    to_encode = ";".join(sorted_values + [secret_key])
    return {"X-TOKEN": md5(to_encode.encode()).hexdigest()}


def get_sport_tree():
    req_url = base_url.format("slice")

    headers = base_headers.copy()
    headers.update(get_xtoken(live_payload))

    r = requests.post(req_url, headers=headers, data=live_payload)
    check_status(r.status_code)
    response = r.json()

    sport_tree = {sport_id: [] for sport_id in sports_by_id.keys()}
    for category in response["data"]:
        sport_id = category["sport_id"]
        if sport_id in sport_tree:
            for event in category["it"]:
                sport_tree[sport_id].append(event["id"])

    return sport_tree


async def get_event_details(event_id, sport_id, session):
    req_url = base_url.format("stakes")

    payload = live_payload.copy()
    payload.update({
        "sport_id": sport_id,
        "id": event_id,
    })

    headers = base_headers.copy()
    headers.update(get_xtoken(payload))

    resp = await async_post(session, req_url, headers=headers, data=payload, allow_not_found=True, allow_blocked=True)

    details = resp["data"] if resp else None
    return {"sport_id": sport_id, "details": details}


def load_events():
    sport_tree = get_sport_tree()

    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession(loop=loop)

    details_task = []
    for sport_id in sport_tree.keys():
        for event_id in sport_tree[sport_id]:
            details_task.append(get_event_details(event_id, sport_id, session))

    details_resp = loop.run_until_complete(asyncio.gather(*details_task))
    session.close()

    events_info = {sport: [] for sport in ("soccer", "basket", "hockey", "tennis", "volley")}
    for event_info in details_resp:
        sport = sports_by_id[event_info["sport_id"]]
        if event_info["details"]:
            events_info[sport].append(event_info["details"])

    log_loaded_events(name)
    return events_info
