import logging

from surebet.main import start_scanning


def test_integration():
    start_scanning(3)

    logging.info("PASS: integration")
