from surebet.loading.olimp import *
from surebet.loading import LoadException
from surebet.betting import get_session_with_proxy

import logging

name = "olimp"

DEFAULT_ACCOUNT = {
    "login": "LOGIN",
    "passw": "PASSWORD",
}


class OlimpBot:
    """Use to place bets on olimp site."""

    def __init__(self, account: dict = DEFAULT_ACCOUNT) -> None:
        self.session = get_session_with_proxy(name)

        self.session_payload = base_payload.copy()

        self.sign_in(account)

    def sign_in(self, account: dict) -> None:
        """Sign in to olimp, remember session id."""
        req_url = base_url.format("autorize")

        payload = base_payload.copy()
        payload.update(account)

        resp = self.session.post(req_url, headers=get_xtoken(payload), data=payload)
        check_status(resp.status_code)

        self.session_payload["session"] = resp.json()["data"]["session"]

    def place_bet(self, amount: int, wager) -> None:
        """
        :param amount: amount of money to be placed (RUB)
        :param wager: defines on which wager bet is to be placed (could be either OlimpWager or OlimpCondWager)
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

        resp = self.session.post(url, headers=headers, data=payload)
        check_status(resp.status_code)
        res = resp.json()
        if "data" not in res or res["data"] != "Your bet is successfully accepted!":
            logging.error(res)
            raise LoadException("error while placing the bet")
