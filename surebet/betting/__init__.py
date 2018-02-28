from requests import Session
from json import load
import os

package_dir = os.path.dirname(__file__)


def get_session_with_proxy(name):
    with open(os.path.join(package_dir, "proxies.json")) as file:
        proxies = load(file)
    session_proxies = proxies[name]

    session = Session()
    # session.proxies = session_proxies

    return session
