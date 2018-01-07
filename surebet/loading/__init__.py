import subprocess

from pyvirtualdisplay import Display
from selenium import webdriver

subprocess.run(['killall', '-s', '9', 'Xvfb'])


# TODO: remove old files


class LoadException(Exception):
    pass


class Selenium:
    def __init__(self) -> None:
        self._display = Display(visible=0, size=(1920, 1080))
        self._display.start()

        self.browser = webdriver.Chrome()

    def quit(self):
        self.browser.quit()

        self._display.stop()
