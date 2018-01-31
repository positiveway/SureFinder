import subprocess

from pyvirtualdisplay import Display
from selenium import webdriver

# kill Chrome at program launch
subprocess.run(['killall', '-s', '9', 'Xvfb'])


# TODO: remove old files

class Selenium:
    def __init__(self, implicit_wait=60) -> None:
        self._display = Display(visible=0, size=(1920, 1080))
        self._display.start()

        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(implicit_wait)

    def quit(self):
        self.browser.quit()

        self._display.stop()
