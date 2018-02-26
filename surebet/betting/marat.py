import logging
from python3_anticaptcha import ImageToTextTask
from requests import Session

from surebet.betting.fonbet import get_dumped_payload
from surebet.loading import browser_headers, check_status, LoadException

ANTICAPTCHA_KEY = "f9e4dd647d31591032ed19dd5d7dfd3d"

DEFAULT_ACCOUNT = {
    "login": "lester0578",
    "pass": "1q1w1e1r1q1w1e1r",
}

COMMON_URL = "https://www.marathonbet.com/en/{}"


class MaratBot:
    def __init__(self, account: dict = DEFAULT_ACCOUNT):
        self.session = Session()

        headers = browser_headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.session.headers.update(headers)

        self.sign_in(account)

    def sign_in(self, account: dict):
        url = COMMON_URL.format("login.htm")

        form_data = {
            "login": account["login"],
            "login_password": account["pass"],
            "captcha": self.get_captcha_code(),
            "loginUrl": "https://www.marathonbet.com:443/en/login.htm"
        }

        resp = self.session.post(url, data=form_data)
        check_status(resp.status_code)
        res = resp.json()
        if "loginResult" not in res or res["loginResult"] != "SUCCESS":
            logging.error(res)
            raise LoadException("failed to sign in")

    def get_captcha_code(self):
        url = COMMON_URL.format("captcha.htm")

        resp = self.session.get(url)
        check_status(resp.status_code)
        with open("captcha.png", "wb") as out:
            out.write(resp.content)

        captcha_answer = ImageToTextTask.ImageToTextTask(anticaptcha_key=ANTICAPTCHA_KEY).captcha_handler(
            captcha_file="captcha.png")

        if "status" in captcha_answer and captcha_answer["status"] != "ready":
            logging.error(captcha_answer)
            raise LoadException("failed to solve captcha")

        return captcha_answer["solution"]["text"]

    def place_bet(self, amount: int, wager):
        url = COMMON_URL.format("betslip/placebet.htm")

        bet_info = [{
            "url": wager.marat_info.factor_id,
            "stake": amount,
            "vip": False,
            "ew": False,
        }]
        form_data = {
            "schd": False,
            "p": "SINGLE",
            "b": get_dumped_payload(bet_info),
        }

        resp = self.session.post(url, data=form_data)
        check_status(resp.status_code)
