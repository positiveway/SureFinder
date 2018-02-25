import os
import json

PACKAGE_DIR = os.path.dirname(__file__)


def read_json(site_name, filename):
    with open(os.path.join(PACKAGE_DIR, site_name, '{}.json'.format(filename))) as f:
        result = json.load(f)
    return result
