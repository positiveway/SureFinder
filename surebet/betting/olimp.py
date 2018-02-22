from surebet.loading.olimp import *
from surebet.loading import LoadException

import logging

DEFAULT_ACCOUNT = {
    "login": "3959858",
    "passw": "O335673J",
}


class OlimpBot:
    """Use to place bets on olimp site."""

    def __init__(self, account: dict = DEFAULT_ACCOUNT) -> None:
        self.session_payload = base_payload.copy()

        self.sign_in(account)

    def sign_in(self, account: dict) -> None:
        """Sign in to olimp, remember session id."""
        req_url = base_url.format("autorize")

        payload = base_payload.copy()
        payload.update(account)

        resp = requests.post(req_url, headers=get_xtoken(payload), data=payload)
        check_status(resp.status_code)

        self.session_payload["session"] = resp.json()["data"]["session"]

    def place_bet(self, amount: int, wager) -> None:
        """
        :param amount: amount of money to be placed (RUB)
        :param wager: defines on which wager bet is to be placed (OlimpWager or OlimpCondWager)
        """
        olimp_info = wager.olimp_info

        url = base_url.format("basket/fast")

        payload = self.session_payload.copy()
        payload.update({
            "coefs_ids": '[["{apid}",{factor},1]]'.format(apid=olimp_info.factor_id, factor=wager.factor),
            "sport_id": olimp_info.sport_id,
            "sum": amount,
            "save_any": 1,
            "fast": 1,
        })

        headers = base_headers.copy()
        headers.update(get_xtoken(payload))

        resp = requests.post(url, headers=headers, data=payload)
        check_status(resp.status_code)
        res = resp.json()
        if "data" not in res or res["data"] != "Your bet is successfully accepted!":
            logging.error(res)
            raise LoadException("error while placing the bet")
