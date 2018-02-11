import surebet.tests.parsing as tester

name = "marat"


def test_samples():
    tester.test_samples(name, 'json')


def test_known_result():
    tester.test_known_result(name, 'knownResultIn.json', 'knownResultOut.json')


def test_broken_structure():
    tester.test_broken_structure(name, 'brokenStructure.json')
