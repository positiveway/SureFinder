import requests
from random import random
import hmac
from hashlib import sha512
from json import dumps

from surebet.loading import *

common_url = "https://clientsapi-003.ccf4ab51771cacd46d.com/session/{}"

login = 4052045
password = "VCqA1CkK"

base_payload = {
    "clientId": login,
    "sysId": 1,
}


def get_dumped_payload(payload):
    dumped = dumps(payload)
    dumped = dumped.replace(": ", ":")  # remove spaces between items
    dumped = dumped.replace(", ", ",")
    return dumped


def _init():
    url = common_url.format("login")

    payload = base_payload.copy()
    payload["random"] = str(random()) + " :))"
    payload["sign"] = "secret password"

    msg = get_dumped_payload(payload)
    sign = hmac.new(key=password.encode(), msg=msg.encode(), digestmod=sha512).hexdigest()
    payload["sign"] = sign

    data = get_dumped_payload(payload)
    resp = requests.post(url, headers=browser_headers, data=data)
    check_status(resp.status_code)
    res = resp.json()
    if "fsid" not in res:
        logging.info(res)
        raise LoadException("key 'fsid' not found in response")

    base_payload["fsid"] = res["fsid"]


_init()

amount = 30
event_id = 9653011
factor_id = 928
value = 1.3
param = 150
score = "0:0"


def place_bet():
    url = common_url.format("coupon/register")
    payload = base_payload.copy()
    payload.update({
        "requestId": get_request_id(),
        "coupon": {
            "flexBet": "up",
            "flexParam": False,
            "bets": [{
                "num": 1,
                "event": event_id,
                "factor": factor_id,
                "value": value,
                "param": param,
                "score": score,
            }]
        }
    })

    check_in_bounds(payload)
    payload["coupon"]["amount"] = amount

    resp = requests.post(url, headers=browser_headers, json=payload)
    check_status(resp.status_code)

    print(resp.text)

    get_result(payload)


def get_request_id():
    url = common_url.format("coupon/requestId")

    resp = requests.post(url, headers=browser_headers, json=base_payload)
    check_status(resp.status_code)
    res = resp.json()
    if "requestId" not in res:
        logging.info(res)
        raise LoadException("key 'requestId' not found in response")

    return res["requestId"]


def check_in_bounds(payload):
    url = common_url.format("coupon/getMinMax")
    payload["coupon"]["amount"] = 0

    resp = requests.post(url, headers=browser_headers, json=payload)
    check_status(resp.status_code)
    res = resp.json()
    if "min" not in res:
        logging.info(res)
        raise LoadException("key 'min' not found in response")

    min_amount, max_amount = res["min"] // 100, res["max"] // 100
    if not (min_amount <= amount <= max_amount):
        logging.info(res)
        raise LoadException("amount is not in bounds")


def get_result(payload):
    url = common_url.format("coupon/result")
    del payload["coupon"]

    resp = requests.post(url, headers=browser_headers, json=payload)
    check_status(resp.status_code)
    res = resp.json()
    # there's situations where "temporary unknown result" means successful response
    if "temporary unknown result" not in resp.text and ("coupon" not in res or res["coupon"]["resultCode"] != 0):
        logging.info(res)
        raise LoadException("response came with an error")

    print(resp.text)
