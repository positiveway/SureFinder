import logging
from unittest.mock import patch

import surebet.betting.fonbet
from surebet.loading.fonbet import name
from surebet.tests.betting import *


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

    # assert gathered data
    assert 'data' in mock_session.post.call_args[1]
    assert_dicts_equal(data, eval(mock_session.post.call_args[1]['data']))
    # assert response correctness
    assert fonbet_bot.base_payload['fsid'] == resp['fsid']


def test_signing():
    data = read_json(name, 'signingData')
    resp = read_json(name, 'signingResp')
    mock_signing(data, resp)

    logging.info('PASS: signing')


def test_placing():
    pass
