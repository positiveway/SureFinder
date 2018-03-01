import logging
from python3_anticaptcha import ImageToTextTask

from surebet.betting.fonbet import get_dumped_payload
from surebet.betting import get_session_with_proxy
from surebet.loading import browser_headers, check_status, LoadException
from surebet.loading.selenium import SeleniumService

name = "marat"

ANTICAPTCHA_KEY = "f9e4dd647d31591032ed19dd5d7dfd3d"

DEFAULT_ACCOUNT = {
    "login": "lester0578",
    "pass": "1q1w1e1r1q1w1e1r",
}

COMMON_URL = "https://www.marathonbet.com/en/{}"


def get_selenium_proxy():
    host = "62.141.38.224"
    port = "65233"
    login = "korovkinandg"
    passw = "L2f8SwJ"

    from zipfile import ZipFile

    from selenium import webdriver

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (host, port, login, passw)

    chrome_options = webdriver.ChromeOptions()

    plugin_file = 'proxy_auth_plugin.zip'

    with ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    chrome_options.add_extension(plugin_file)

    return webdriver.Chrome(chrome_options=chrome_options)


def get_selenium_proxy_without_auth():
    from selenium import webdriver

    PROXY = "http://62.141.38.224:65233"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=%s' % PROXY)

    return webdriver.Chrome(chrome_options=chrome_options)


class MaratBot:
    def __init__(self, account: dict = DEFAULT_ACCOUNT):
        self.session = get_session_with_proxy(name)

        headers = browser_headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.session.headers.update(headers)

        SeleniumService()
        self.browser = get_selenium_proxy()  # SeleniumService().new_instance().browser
        self.browser.implicitly_wait(60)

        self.sign_in(account)

    def sign_in(self, account: dict):
        url = COMMON_URL.format("login.htm")

        form_data = {
            "login": account["login"],
            "login_password": account["pass"],
            "captcha": self._get_captcha_code(),
            "loginUrl": "https://www.marathonbet.com:443/en/login.htm"
        }

        resp = self.session.post(url, data=form_data)
        check_status(resp.status_code)
        res = resp.json()
        if "loginResult" not in res or res["loginResult"] != "SUCCESS":
            logging.error(res)
            raise LoadException("failed to sign in")

        self._set_up_browser()

    def _set_up_browser(self):
        url = COMMON_URL.format("live")
        self.browser.get(url)
        self.browser.get_screenshot_as_file("first.png")

        for key, val in self.session.cookies.get_dict().items():
            self.browser.add_cookie({"name": key, "value": val})

        self.browser.get(url)
        self.browser.get_screenshot_as_file("second.png")

    def _get_captcha_code(self):
        url = COMMON_URL.format("captcha.htm")

        resp = self.session.get(url)
        check_status(resp.status_code)
        with open("captcha.png", "wb") as out:
            out.write(resp.content)

        captcha_answer = ImageToTextTask.ImageToTextTask(anticaptcha_key=ANTICAPTCHA_KEY).captcha_handler(
            captcha_file="captcha.png")

        if "status" in captcha_answer and captcha_answer["status"] != "ready":
            logging.error(captcha_answer)
            raise LoadException("failed to solve captcha")

        return captcha_answer["solution"]["text"]

    def place_bet(self, amount: int, wager):
        url = COMMON_URL.format("betslip/placebet.htm")

        bet_info = [{
            "url": wager.marat_info.factor_id,
            "stake": amount,
            "vip": False,
            "ew": False,
        }]
        form_data = {
            "schd": "false",
            "p": "SINGLES",
            "b": get_dumped_payload(bet_info),
        }

        self._update_cookies()

        resp = self.session.post(url, data=form_data)
        print(resp.text)
        check_status(resp.status_code)

    def _update_cookies(self):
        cookies = {}
        for cookie in self.browser.get_cookies():
            cookies[cookie["name"]] = cookie["value"]
        self.session.cookies.update(cookies)
