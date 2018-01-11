import subprocess

from pyvirtualdisplay import Display
from selenium import webdriver

subprocess.run(['killall', '-s', '9', 'Xvfb'])


# TODO: remove old files


class LoadException(Exception):
    pass


def check_status(site_name, status_code):
    if status_code != 200:
        raise LoadException("{} is not responding".format(site_name))


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
