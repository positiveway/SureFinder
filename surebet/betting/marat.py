import logging
from python3_anticaptcha import ImageToTextTask

from surebet.betting.fonbet import get_dumped_payload
from surebet.betting import get_session_with_proxy
from surebet.loading import browser_headers, check_status, LoadException

name = "marat"

ANTICAPTCHA_KEY = "f9e4dd647d31591032ed19dd5d7dfd3d"

DEFAULT_ACCOUNT = {
    "login": "lester0578",
    "pass": "1q1w1e1r1q1w1e1r",
}

COMMON_URL = "https://www.marathonbet.com/en/{}"

LOCAL = True


class MaratBot:
    def __init__(self, account: dict = DEFAULT_ACCOUNT):
        self.session = get_session_with_proxy(name)

        headers = browser_headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.session.headers.update(headers)

        from pickle import load, dump
        if not LOCAL:
            self.sign_in(account)

            mode = "wb"
            with open("headers", mode) as out:
                dump(self.session.headers, out)

            with open("cookies", mode) as out:
                new_cookies = {}
                for k, v in self.session.cookies.items():
                    k = k.upper()
                    if k == "SESSION_KEY" or "PUNTER" in k:
                        new_cookies[k] = v

                self.session.cookies.clear()
                self.session.cookies.update(new_cookies)

                dump(self.session.cookies, out)

            exit(0)
        else:
            mode = "rb"
            with open("headers", mode) as out:
                headers = load(out)
                self.session.headers = headers

            with open("cookies", mode) as out:
                cookies = load(out)
                self.session.cookies = cookies

    def sign_in(self, account: dict):
        url = COMMON_URL.format("login.htm")

        form_data = {
            "login": account["login"],
            "login_password": account["pass"],
            "captcha": self._get_captcha_code(),
            "loginUrl": "https://www.marathonbet.com:443/en/login.htm"
        }

        resp = self.session.post(url, data=form_data)
        check_status(resp.status_code)
        res = resp.json()
        if "loginResult" not in res or res["loginResult"] != "SUCCESS":
            logging.error(res)
            raise LoadException("failed to sign in")

    def _get_captcha_code(self):
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
            "schd": "false",
            "p": "SINGLES",
            "b": get_dumped_payload(bet_info),
        }

        print(self.session.cookies.get_dict())

        del self.session.cookies["SESSION_KEY"]

        resp = self.session.post(url, data=form_data, verify=False)  # sending outdated request to set actual cookies
        # print(resp.text)

        print(self.session.cookies.get_dict())

        resp = self.session.post(url, data=form_data, verify=False)
        print(self.session.cookies.get_dict())
        # print(resp.text)
        check_status(resp.status_code)
