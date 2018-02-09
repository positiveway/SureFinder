import os

from surebet.loading import LoadException

package_dir = os.path.dirname(__file__)


def check_result(result, min_size=0):
    result_size = len(result)
    if result_size <= min_size:
        raise LoadException("result with small size")
    else:
        print(result_size)
