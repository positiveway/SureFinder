from traceback import format_exc

import os

from surebet import package_dir


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


def log_loaded(site_name):
    print("{}: loaded".format(site_name))


def log_loaded_events(site_name):
    print("{}: loaded events".format(site_name))


def handle_loading_err(browser, name):
    browser.get_screenshot_as_file("{}-error.png".format(name))
    raise LoadException("{} is not responding".format(name))
