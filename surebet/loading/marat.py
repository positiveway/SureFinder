import re
import requests
import json
import asyncio
import aiohttp
import async_timeout

from surebet.loading import check_status, log_loaded

name = "marat"

url = "https://www.marathonbet.co.uk/en/live"
live_elem = "#container_AVAILABLE > div"

sports = ["45356", "26418", "43658", "22723", "23690"]
sport_names = ["Basketball", "Football", "Ice Hockey", "Tennis", "Volleyball"]

details_url = "https://www.marathonbet.co.uk/en/livemarkets.htm?treeId={}"

TIMEOUT = 10


def load_events():
    r = requests.get(url)
    check_status(name, r.status_code)

    site_html = r.text
    res = re.search(r"reactData = ({.*});", site_html)
    raw_sport_tree = json.loads(res.group(1))["liveMenuEvents"]["childs"]

    sport_tree = process_sport_tree(raw_sport_tree)

    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession(loop=loop)

    details_task = []
    add_info_task = []
    for sport in sport_tree:
        if sport["name"] == "Tennis" or sport["name"] == "Volleyball":
            add_info_task.append(get_add_info(sport["id"], sport["name"], session))
        for event in sport["events"]:
            details_task.append(get_event_details(event["id"], session))

    details_resp, add_info_resp = loop.run_until_complete(asyncio.gather(
        asyncio.gather(*details_task),
        asyncio.gather(*add_info_task),
    ))
    session.close()

    details = [detail for detail in details_resp if detail]
    add_infos = {}
    for add_info in add_info_resp:
        if add_info["html"]:
            add_infos[add_info["sport"]] = add_info["html"]

    log_loaded(name)
    return {"events": details, "add_info": add_infos, "sport_tree": sport_tree}


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


async def get_event_details(event_id, session):
    req_url = details_url.format(event_id)

    return await post_req(session, req_url)


async def post_req(session, url):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    with async_timeout.timeout(TIMEOUT):
        async with session.post(url, headers=headers) as response:
            if response.status == 204:
                return None
            check_status(name, response.status)

            result = await response.json(content_type=response.content_type)
            return result["ADDITIONAL_MARKETS"]


async def get_add_info(sport_id, sport_name, session):
    req_url = url + "/{}".format(sport_id)

    return {"sport": sport_name, "html": await get_req(session, req_url)}


async def get_req(session, url):
    with async_timeout.timeout(TIMEOUT):
        async with session.get(url) as response:
            check_status(name, response.status)
            return await response.text()
