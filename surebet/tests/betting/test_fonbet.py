import logging
from unittest.mock import patch, MagicMock

from surebet.loading.fonbet import name
import surebet.betting.fonbet
from surebet.tests.betting import read_json


class MockResponse(MagicMock):
    def __init__(self, resp):
        super().__init__()
        self.status_code = 200
        self.json = MagicMock()
        self.json.return_value = resp


class MockSession(MagicMock):
    def __init__(self, resp):
        super().__init__()
        self.post = MagicMock()
        self.post.return_value = MockResponse(resp)


@patch('surebet.betting.fonbet.get_session_with_proxy')
@patch('surebet.betting.fonbet.get_common_url')
@patch('surebet.betting.fonbet.random')
def mock_signing(data, resp, mock_random, mock_url, mock_proxy):
    random_val = float(data['random'].split()[0])
    url_login = 'https://clientsapi-003.ccf4ab51771cacd46d.com/session/{}'

    mock_random.return_value = random_val
    mock_url.return_value = url_login
    mock_session = MockSession(resp)
    mock_proxy.return_value = mock_session
    fonbet_bot = surebet.betting.fonbet.FonbetBot()

    # check gathered data
    assert 'data' in mock_session.post.call_args[1]
    data_called = eval(mock_session.post.call_args[1]['data'])
    for key, value in data_called.items():
        assert key in data and value == data[key]
    # check response correctness
    assert fonbet_bot.base_payload['fsid'] == '5geiQm1banahlLIQrNpBBi81'


def test_sign_in():
    data = read_json(name, 'signingData')
    resp = read_json(name, 'signingResp')
    mock_signing(data, resp)

    logging.info('PASS: signing')


def test_place_bet():
    pass
