import os

from surebet import package_dir
from surebet.loading import LoadException


def try_load_events(load_func, site_name, **kwargs):
    try:
        result = load_func(**kwargs)
    except LoadException as e:
        filename = os.path.join(package_dir, "error-loading-{}".format(site_name))
        with open(filename, "w") as out:
            out.write(str(e))
        raise
    return result


def check_result(result, min_size=0):
    result_size = len(result)
    if result_size <= min_size:
        raise LoadException("result with small size")
    else:
        print(result_size)
