import requests
from random import random
import hmac
from hashlib import sha512
from json import dumps

from surebet.betting import get_session_with_proxy
from surebet.loading import *
from surebet.handling.surebets import FonbetCondWager

name = "fonbet"

DEFAULT_ACCOUNT = {
    "login": 4052045,
    "password": "VCqA1CkK",
}


def get_dumped_payload(payload):
    dumped = dumps(payload)
    dumped = dumped.replace(": ", ":")  # remove spaces between items
    dumped = dumped.replace(", ", ",")
    return dumped


def get_urls():
    url = "https://www.fonbet.com/urls.json?{}".format(random())
    resp = requests.get(url, headers=browser_headers)
    check_status(resp.status_code)

    return resp.json()


def get_common_url():
    urls = get_urls()

    client_url = urls["clients-api"][0]

    return "https:{url}/session/".format(url=client_url) + "{}"


class FonbetBot:
    """Use to place bets on fonbet site."""

    def __init__(self, account: dict = DEFAULT_ACCOUNT) -> None:
        self.session = get_session_with_proxy(name)

        self.common_url = get_common_url()

        self.base_payload = {
            "sysId": 1,
        }

        self.sign_in(account)

    def sign_in(self, account: dict) -> None:
        """Sign in to fonbet, remember session id and client id."""
        url = self.common_url.format("login")

        self.base_payload["clientId"] = account["login"]

        payload = self.base_payload.copy()
        payload["random"] = str(random()) + " :))"
        payload["sign"] = "secret password"

        msg = get_dumped_payload(payload)
        sign = hmac.new(key=account["password"].encode(), msg=msg.encode(), digestmod=sha512).hexdigest()
        payload["sign"] = sign

        data = get_dumped_payload(payload)
        resp = self.session.post(url, headers=browser_headers, data=data)
        check_status(resp.status_code)
        res = resp.json()
        if "fsid" not in res:
            logging.error(res)
            raise LoadException("key 'fsid' not found in response")

        self.base_payload["fsid"] = res["fsid"]

    def place_bet(self, amount: int, wager) -> None:
        """
        :param amount: amount of money to be placed (RUB)
        :param wager: defines on which wager bet is to be placed (could be either FonbetWager or FonbetCondWager)
        """
        fonbet_info = wager.fonbet_info

        url = self.common_url.format("coupon/register")
        payload = self.base_payload.copy()
        payload.update({
            "requestId": self._get_request_id(),
            "coupon": {
                "flexBet": "up",
                "flexParam": False,
                "bets": [{
                    "num": 1,
                    "event": fonbet_info.event_id,
                    "factor": fonbet_info.factor_id,
                    "value": wager.factor,
                    "score": fonbet_info.score,
                }]
            }
        })

        if isinstance(wager, FonbetCondWager):  # if wager has condition and it should be in payload
            payload["coupon"]["bets"][0]["param"] = int(wager.cond * 100)

        self._check_in_bounds(payload, amount)
        payload["coupon"]["amount"] = amount

        resp = self.session.post(url, headers=browser_headers, json=payload)
        check_status(resp.status_code)

        self._check_result(payload)

    def _get_request_id(self) -> int:
        """request_id is generated every time we placing bet"""
        url = self.common_url.format("coupon/requestId")

        resp = self.session.post(url, headers=browser_headers, json=self.base_payload)
        check_status(resp.status_code)
        res = resp.json()
        if "requestId" not in res:
            logging.error(res)
            raise LoadException("key 'requestId' not found in response")

        return res["requestId"]

    def _check_in_bounds(self, payload: dict, amount: int) -> None:
        """Check if amount is in allowed bounds"""
        url = self.common_url.format("coupon/getMinMax")
        payload["coupon"]["amount"] = 0

        resp = self.session.post(url, headers=browser_headers, json=payload)
        check_status(resp.status_code)
        res = resp.json()
        if "min" not in res:
            logging.info(res)
            raise LoadException("key 'min' not found in response")

        min_amount, max_amount = res["min"] // 100, res["max"] // 100
        if not (min_amount <= amount <= max_amount):
            logging.error(res)
            raise LoadException("amount is not in bounds")

    def _check_result(self, payload: dict) -> None:
        """Check if bet is placed successfully"""
        url = self.common_url.format("coupon/result")
        del payload["coupon"]

        resp = self.session.post(url, headers=browser_headers, json=payload)
        check_status(resp.status_code)
        res = resp.json()
        # there's situations where "temporary unknown result" means successful response
        if "temporary unknown result" not in resp.text and ("coupon" not in res or res["coupon"]["resultCode"] != 0):
            logging.error(res)
            raise LoadException("response came with an error")
