import os
import json
from unittest.mock import MagicMock

PACKAGE_DIR = os.path.dirname(__file__)


def read_json(site_name, filename):
    with open(os.path.join(PACKAGE_DIR, site_name, '{}.json'.format(filename))) as f:
        result = json.load(f)
    return result


def assert_dicts_equal(dict1, dict2):
    for key, value in dict1.items():
        assert key in dict2
        if not isinstance(value, dict):
            assert value == dict2[key]
        else:
            assert_dicts_equal(value, dict2[key])


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
