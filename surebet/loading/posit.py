from json import load
from os import path
from random import choice, seed

from lxml import html

from surebet.loading import *
from surebet.parsing import xpath_with_check

# TODO: replace by mock
# temporary generates random account
seed()
with open(path.join(package_dir, "accounts.json")) as file:
    accounts = load(file)
default_account = choice(accounts)

name = "positivebet"
login_url = "https://positivebet.com/en/user/login"
index_url = "https://positivebet.com/en/bets/index"

xp_token = '//*[@id="login-form"]/input'
token_name = "YII_CSRF_TOKEN"

payload = {
    "UserLogin[rememberMe]": ["0", "1"],
    "yt0": '',
}

cookies = {
    "ddlPerPage_value": "30",
}


def load(session, account=default_account):
    payload.update({
        "UserLogin[username]": account["login"],
        "UserLogin[password]": account["pass"],
    })

    session.headers.update(browser_headers)

    resp = session.get(login_url)
    check_status(resp.status_code)

    payload[token_name] = _get_token(resp.text)

    resp = session.post(login_url, data=payload)
    check_status(resp.status_code)

    session.cookies.update(cookies)

    log_loaded(name)


def _get_token(source):
    doc = html.fromstring(source)

    token_node = xpath_with_check(doc, xp_token)[0]
    return token_node.get("value")


def load_events(session):
    resp = session.get(index_url)
    check_status(resp.status_code)

    log_loaded_events(name)
    return resp.text
