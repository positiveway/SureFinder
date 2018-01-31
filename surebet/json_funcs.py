import json

_json_params = {'indent': 2, 'sort_keys': True}
_convert_func = {'default': lambda o: o.__dict__}


def json_dump(obj, fp, **kwargs):
    json.dump(obj, fp, **_json_params, **kwargs)


def json_dumps(obj, **kwargs):
    return json.dumps(obj, **_json_params, **kwargs)


def obj_dump(obj, fp):
    return json_dump(obj, fp, **_convert_func)


def obj_dumps(obj):
    return json_dumps(obj, **_convert_func)
