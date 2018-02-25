import logging
from unittest.mock import patch

import surebet.betting.olimp
from surebet.loading.olimp import name
from surebet.tests.betting import *


@patch('surebet.betting.olimp.get_session_with_proxy')
def mock_signing(data, headers, resp, mock_proxy):
    mock_session = MockSession(resp)
    mock_proxy.return_value = mock_session

    olimp_bot = surebet.betting.olimp.OlimpBot()

    # check gathered data and headers
    assert 'data' in mock_session.post.call_args[1]
    assert_dicts_equal(data, mock_session.post.call_args[1]['data'])
    assert 'headers' in mock_session.post.call_args[1]
    assert_dicts_equal(headers, mock_session.post.call_args[1]['headers'])
    # check response correctness
    assert olimp_bot.session_payload['session'] == resp['data']['session']


def test_signing():
    data = read_json(name, 'signingData')
    headers = read_json(name, 'signingHeaders')
    resp = read_json(name, 'signingResp')
    mock_signing(data, headers, resp)

    logging.info('PASS: signing')


def test_placing():
    pass
