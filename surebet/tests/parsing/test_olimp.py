import pytest
from os import path

from surebet import *
from surebet.parsing import ParseException
from surebet.parsing.olimp import parse
from surebet.tests.parsing import *

resource_dir = path.join(package_dir, 'olimp')


def abs_path(filename):
    return path.join(resource_dir, filename)


def test_samples():
    for num in range(3):
        filename = abs_path('sample{}.html'.format(num))
        with open(filename, encoding='utf-8') as file:
            html = file.read()
        parse(html)
        logging.info('PASS: sample{}'.format(num))


def test_known_result():
    filename = abs_path('knownResult.json')
    with open(filename, encoding='utf-8') as file:
        known_result = json.load(file)

    filename = abs_path('knownResult.html')
    with open(filename, encoding='utf-8') as file:
        html = file.read()

    olimp = parse(html)
    olimp.format()

    assert obj_to_json(olimp) == json_dumps(known_result)

    logging.info('PASS: known result')


def test_broken_structure():
    filename = abs_path('brokenStructure.html')
    with open(filename, encoding='utf-8') as file:
        html = file.read()

    with pytest.raises(ParseException, message='Expecting ParseException'):
        parse(html)

    logging.info('PASS: broken structure')

if __name__ == '__main__':
    # test_samples()
    # test_broken_structure()
    test_known_result()

    # filename = abs_path('knownResult.html')
    # with open(filename, encoding='utf-8') as file:
    #     html = file.read()
    #
    # olimp = parse(html)
    # olimp.format()
    #
    # with open(abs_path('knownResult.json'), 'w', encoding='utf-8') as json_file:
    #     json_file.write(obj_to_json(olimp))
