from surebet.loading.olimp import *
from surebet.loading import LoadException

import logging

login = "3959858"
passw = "O335673J"

session_payload = base_payload.copy()


def _init():
    req_url = base_url.format("autorize")

    payload = base_payload.copy()
    payload.update({
        "login": login,
        "passw": passw,
    })

    resp = requests.post(req_url, headers=get_xtoken(payload), data=payload)
    check_status(resp.status_code)

    session_payload["session"] = resp.json()["data"]["session"]


_init()

factor_id = "906824311:38209913:3:7:2.5:1:0:0:1"
sport_id = 1
sum = 10
factor = 1.17


def place_bet():
    url = base_url.format("basket/fast")

    payload = session_payload.copy()
    payload.update({
        "coefs_ids": '[["{apid}",{factor},1]]'.format(apid=factor_id, factor=factor),
        "sport_id": sport_id,
        "sum": sum,
        "save_any": 1,
        "fast": 1,
    })

    headers = base_headers.copy()
    headers.update(get_xtoken(payload))

    resp = requests.post(url, headers=headers, data=payload)
    print(resp.text)
    check_status(resp.status_code)
    res = resp.json()
    if "data" not in res or res["data"] != "Your bet is successfully accepted!":
        logging.info(res)
        raise LoadException("error while placing the bet")
