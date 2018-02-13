import surebet.tests.parsing as tester


def test_fonbet():
    tester.test_bookmaker('fonbet', 'html')


def test_marat():
    tester.test_bookmaker('marat', 'json')


def test_olimp():
    tester.test_bookmaker('olimp', 'json')
