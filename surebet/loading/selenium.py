import subprocess

from pyvirtualdisplay import Display
from selenium import webdriver


def _kill_all(process: str) -> None:
    command = ['killall', '-s', '9']
    subprocess.run(command + [process])


class Selenium:
    def __init__(self, implicit_wait=60) -> None:
        self.browser = Display(visible=0, size=(1920, 1080))
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(implicit_wait)

    def quit(self):
        self.browser.quit()


class SeleniumService:
    _pool = []
    _first_run = True

    def __init__(self):
        if SeleniumService._first_run:
            SeleniumService._first_run = False

            # kill Chrome at program launch
            _kill_all('Xvfb')
            _kill_all('chromedriver')

            Display(visible=0, size=(1920, 1080)).start()

            # TODO: remove old resource files (png, html, etc)

    @staticmethod
    def new_instance():
        SeleniumService._pool.append(Selenium())
        return SeleniumService._pool[-1]

    @staticmethod
    def quit():
        for instance in SeleniumService._pool:
            instance.quit()
        SeleniumService._pool.clear()
