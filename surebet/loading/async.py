import async_timeout

from surebet.loading import check_status, LoadException

TIMEOUT = 10


async def _async_req(method, handler, url, **kwargs):
    headers = kwargs.get('headers', None)
    data = kwargs.get('data', None)
    allow_empty = kwargs.get('allow_empty', False)
    allow_not_found = kwargs.get('allow_not_found', False)
    allow_blocked = kwargs.get('allow_blocked', False)
    timeout = kwargs.get('timeout', TIMEOUT)

    with async_timeout.timeout(timeout):
        async with method(url, data=data, headers=headers) as response:
            if (allow_empty and response.status == 204) or (allow_not_found and response.status == 404) \
                    or (allow_blocked and response.status == 500):
                return None

            try:
                check_status(response.status)
            except LoadException as e:
                error_text = "response text: {}".format(await response.text())
                raise LoadException(error_text) from e

            return await handler(response)


async def async_post(session, url, **kwargs):
    def handler(resp):
        return resp.json(content_type=resp.content_type)

    return await _async_req(session.post, handler, url, **kwargs)


async def async_get(session, url, **kwargs):
    def handler(resp):
        return resp.text()

    return await _async_req(session.get, handler, url, **kwargs)
