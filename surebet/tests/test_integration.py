import logging

from surebet.main import start_scanning


def test_integration():
    start_scanning()

    logging.info("PASS: integration")
