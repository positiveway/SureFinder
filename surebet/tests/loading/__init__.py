from surebet.loading import LoadException


def check_result(result, min_size=0):
    result_size = len(result)
    if result_size <= min_size:
        raise LoadException("result with small size")
    else:
        print(result_size)
