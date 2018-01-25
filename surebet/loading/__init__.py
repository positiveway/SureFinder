import subprocess
from traceback import format_exc

import async_timeout
import os
from pyvirtualdisplay import Display
from selenium import webdriver

from surebet import package_dir

# kill Chrome at program launch
subprocess.run(['killall', '-s', '9', 'Xvfb'])
# TODO: remove old files

TIMEOUT = 10


class LoadException(Exception):
    pass


def try_load(load_func, site_name, **kwargs):
    try:
        result = load_func(**kwargs)
    except LoadException:
        filename = os.path.join(package_dir, "error-loading-{}".format(site_name))
        with open(filename, "w") as out:
            out.write(format_exc())
        raise
    return result


def check_status(status_code):
    if status_code != 200:
        raise LoadException("Site is not responding, status code: {}".format(status_code))


async def _async_req(method, handler, url, **kwargs):
    headers = kwargs.get('headers', None)
    data = kwargs.get('data', None)
    allow_empty = kwargs.get('allow_empty', False)
    allow_not_found = kwargs.get('allow_not_found', False)
    timeout = kwargs.get('timeout', TIMEOUT)

    with async_timeout.timeout(timeout):
        async with method(url, data=data, headers=headers) as response:
            if (allow_empty and response.status == 204) or (allow_not_found and response.status == 404):
                return None

            try:
                check_status(response.status)
            except LoadException as e:
                error_text = "response text: {}".format(await response.text())
                raise LoadException(error_text) from e

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
    print("{}: loaded".format(site_name))


def log_loaded_events(site_name):
    print("{}: loaded events".format(site_name))


class Selenium:
    def __init__(self, implicit_wait=60) -> None:
        self._display = Display(visible=0, size=(1920, 1080))
        self._display.start()

        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(implicit_wait)

    def quit(self):
        self.browser.quit()

        self._display.stop()


def handle_loading_err(browser, name):
    browser.get_screenshot_as_file("{}-error.png".format(name))
    raise LoadException("{} is not responding".format(name))
