from requests import Session
from surebet.betting.fonbet import get_dumped_payload
from surebet.loading import browser_headers, check_status


class MaratBot:
    def __init__(self):
        self.session = Session()

        headers = browser_headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.session.headers.update(headers)

        self.sign_in()

    def sign_in(self):
        pass  # TODO: get around captcha

    def place_bet(self, amount: int, wager):
        url = "https://www.marathonbet.com/en/betslip/placebet.htm"

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
