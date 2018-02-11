import surebet.tests.parsing as tester

name = "posit"


def test_samples():
    tester.test_samples(name, 'html')


def test_known_result():
    tester.test_known_result(name, 'knownRes.html', 'knownRes.json')


def test_broken_structure():
    tester.test_broken_structure(name, 'brokenStruct.html')
