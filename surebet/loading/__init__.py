import logging
from traceback import format_exc

import os

from surebet import project_dir

package_dir = os.path.dirname(__file__)


class LoadException(Exception):
    pass


def try_load(load_func, site_name, **kwargs):
    try:
        result = load_func(**kwargs)
    except Exception as err:
        if not isinstance(err, KeyboardInterrupt):  # if it wasn't a forced stop of a program
            logging.info("error occurred in loading({}): {}".format(site_name, str(err)))

            filename = os.path.join(project_dir, "error-loading-{}".format(site_name))
            with open(filename, "w") as out:
                out.write(format_exc())
        raise
    return result


def check_status(status_code):
    if status_code != 200:
        raise LoadException("Site is not responding, status code: {}".format(status_code))


def log_loaded(site_name):
    logging.info("{}: loaded".format(site_name))


def log_loaded_events(site_name):
    logging.info("{}: loaded events".format(site_name))


def handle_loading_err(browser, name):
    browser.get_screenshot_as_file("{}-error.png".format(name))
    raise LoadException("{} is not responding".format(name))
