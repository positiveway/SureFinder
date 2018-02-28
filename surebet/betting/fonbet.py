import requests
from random import random, choice
import hmac
from hashlib import sha512
from json import dumps, load
from os import path

from surebet.betting import get_session_with_proxy, package_dir as betting_dir
from surebet.loading import *
from surebet.handling.surebets import FonbetCondWager

name = "fonbet"

DEFAULT_ACCOUNT = {
    "login": 4052045,
    "password": "VCqA1CkK",
}

DEVICE_ID = {"deviceid": "A5-f8fa8b79c4ca4938"}
PLATFORM = {"platform": "mobile_android"}
SYS_ID = {"sysId": 4}
LANG = {"lang": "en"}
TOKEN = {"token": "eM5aX9SaQFQ:APA91bH3MGDCqKEjGQBbjpXxf07x1T_OLpEp6xcw_0HOer0F1B5K5y-CD9hmKgmLY3oKELHFW6VukEeu34awuz1-r2A8VKq4hn0sQFJJ_okGrG8vYkFYvSIXWQst_UFG5yaOtHsVyf6N"}
BET = {
    "appVersion": "v. 4.6.7b (467)",
    "deviceManufacturer": "Meizu",
    "deviceModel": "m3",
}

CONTENT_TYPE = {
    "json": {"Content-Type": "application/json; charset=UTF-8"},
    "plain": {"Content-Type": "application/text"},
    "bin": {"Content-Type": "application/octet-stream"}
}

FONBET_HEADERS = {
    "User-Agent": "Fonbet/4.6.7b (Android; Phone; com.bkfonbet)",
    "Content-Type": "application/json; charset=UTF-8",
    "Accept-Encoding": "gzip",
    "Connection": "Keep-Alive"
}

FONBET_LOGIN_URL = "https://23.111.18.92/session/login?lang=eng"

APPSFLYER = {
    "User-Agent": {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1; m3 Build/LMY47I)"},
    "url_stats": "https://stats.appsflyer.com/stats",
    "url_android": "https://t.appsflyer.com/api/v4/androidevent?buildnumber=3.2&app_id=com.bkfonbet",
    "data_stats": "platform=Android&gcd_conversion_data_timing=8&devkey=xKU2sDi5jALL7PNtqvbUZb&statType=user_closed_app&time_in_app=1468&deviceFingerPrintId=ffffffff-bde3-9677-ffff-ffffcaa88cda&app_id=com.bkfonbet&uid=1517994135280-1947177950217391747&launch_counter=25"
}

FLURRY_URL = "https://data.flurry.com/aap.do"


def get_random_str():
    result = ''
    alph_num = '0123456789'
    alph = 'abcdefghijklmnopqrstuvwxyz'
    alph = alph + alph.upper() + alph_num
    for _idx in range(48):
        result += choice(alph)
    return result


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
        self._sign_in_analytics()

        url = self.common_url.format("login")

        self.base_payload["clientId"] = account["login"]

        filename = path.join(betting_dir, 'payload.json')
        with open(filename) as f_payload:
            payload = load(f_payload)

        payload.update(self.base_payload)
        payload["random"] = get_random_str()
        payload["sign"] = "secret password"

        msg = get_dumped_payload(payload)
        sign = hmac.new(key=account["password"].encode(), msg=msg.encode(), digestmod=sha512).hexdigest()
        payload["sign"] = sign

        data = get_dumped_payload(payload)
        resp = self.session.post(FONBET_LOGIN_URL, headers=FONBET_HEADERS, data=data, verify=False)
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

    def _sign_in_analytics(self):
        headers = APPSFLYER["User-Agent"].update(CONTENT_TYPE["plain"])
        resp = self.session.post(APPSFLYER["url_stats"], data=APPSFLYER["data_stats"], headers=headers)
        check_status(resp.status_code)

        filename_flurry = path.join(betting_dir, 'aap.do')
        with open(filename_flurry, 'rb') as f_flurry:
            data = f_flurry.read()

        headers = APPSFLYER["User-Agent"].update(CONTENT_TYPE["bin"])
        resp = self.session.post(FLURRY_URL, data=data, headers=headers)
        check_status(resp.status_code)

        filename_flyer = path.join(betting_dir, 'appsflyer.json')
        with open(filename_flyer) as f_flyer:
            data = f_flyer.read()

        headers = APPSFLYER["User-Agent"].update(CONTENT_TYPE["json"])
        resp = self.session.post(APPSFLYER["url_android"], data=data, headers=headers)
        check_status(resp.status_code)

        if resp.text != '"ok"':
            raise LoadException("Stats didn't accepted")


FonbetBot()
