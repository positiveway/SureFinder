import logging

from surebet.main import start_scanning


def test_integration():
    for _ in start_scanning(3):
        pass

    logging.info("PASS: integration")
