import requests
from lxml import html

from surebet.loading import check_status, log_loaded

name = "olimp"

xp_event_ids = '//tr[@data-kek="row"]/td/input[1]'


def load_events():
    result = get_events_html(get_event_ids())
    log_loaded(name)
    return result


def get_event_ids():
    req_url = "https://olimp.com/betting"

    r = requests.post(req_url, headers={"cookie": "curr_lang=2;"})
    check_status(r.status_code)

    site_doc = html.fromstring(r.text)

    event_ids = []
    for event_node in site_doc.xpath(xp_event_ids):
        event_id = event_node.get("value")
        event_ids.append(event_id)
    return event_ids


def get_events_html(event_ids):
    req_url = "https://olimp.com/index.php"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "cookie": "curr_lang=2;"
    }

    form_data = {
        "page": "line",
        "action": "2",
        "live[]": event_ids,
    }

    r = requests.post(req_url, headers=headers, data=form_data)
    check_status(r.status_code)

    return r.text
