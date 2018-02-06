import logging
import pickle

from os import path

from surebet.tests.handling import package_dir

from surebet.handling.excluding import exclude_posit

resource_dir = path.join(package_dir, "excluding")


def read_sample(filename):
    found_file = open(path.join(resource_dir, filename), "rb")
    return pickle.load(found_file)


def test_known_result():
    other_surebets = read_sample('known_other.pkl')
    posit_surebets = read_sample('known_posit.pkl')
    result_surebets = read_sample('known_result.pkl')

    exclude_posit(other_surebets, posit_surebets)

    # compare above-computed result with known result
    assert len(other_surebets.books_surebets) == len(result_surebets.books_surebets)
    for os, rs in zip(other_surebets.books_surebets, result_surebets.books_surebets):
        # compare BookSurebets
        assert os == rs
        # compare EventSurebets in BookLevel attributes' list
        ad_os = os.attrs_dict()
        ad_rs = rs.attrs_dict()
        assert sum(1 for sport in ad_os if ad_os[sport] == ad_rs[sport])

    logging.info("PASS: excluding known result")


def test_sample():
    for i in range(2):
        other_surebets = read_sample('sample{0}_other.pkl'.format(i))
        posit_surebets = read_sample('sample{0}_posit.pkl'.format(i))
        exclude_posit(other_surebets, posit_surebets)

    logging.info("PASS: excluding samples")
