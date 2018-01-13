import subprocess

from pyvirtualdisplay import Display
from selenium import webdriver
import async_timeout

# kill Chrome at program launch
subprocess.run(['killall', '-s', '9', 'Xvfb'])
# TODO: remove old files

TIMEOUT = 10


class LoadException(Exception):
    pass


def check_status(status_code):
    if status_code != 200:
        raise LoadException("Site is not responding")


async def _async_req(method, handler, url, **kwargs):
    headers = kwargs.get('headers', None)
    allow_empty = kwargs.get('allow_empty', False)
    timeout = kwargs.get('timeout', TIMEOUT)

    with async_timeout.timeout(timeout):
        async with method(url, headers=headers) as response:
            if allow_empty and response.status == 204:
                return None
            check_status(response.status)

            return await handler(response)


async def async_post(session, url, **kwargs):
    def handler(resp):
        return resp.json(content_type=resp.content_type)

    return await _async_req(session.post, handler, url, **kwargs)


async def async_get(session, url, **kwargs):
    def handler(resp):
        return resp.text()

    return await _async_req(session.get, handler, url, **kwargs)


def log_loaded(site_name):
    print("{}: loaded events".format(site_name))


class Selenium:
    def __init__(self) -> None:
        self._display = Display(visible=0, size=(1920, 1080))
        self._display.start()

        self.browser = webdriver.Chrome()

    def quit(self):
        self.browser.quit()

        self._display.stop()
