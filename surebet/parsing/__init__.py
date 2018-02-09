from re import search

import os
import logging
from traceback import format_exc

from surebet import project_dir
from surebet.json_funcs import obj_dumps


def try_parse(parse_func, source, site_name, **kwargs):
    try:
        result = parse_func(source, **kwargs)
    except Exception as err:
        if not isinstance(err, KeyboardInterrupt):  # if it wasn't a forced stop of a program
            logging.info("error occurred in parsing({}): {}".format(site_name, str(err)))

            filename = os.path.join(project_dir, "error-parsing-{}".format(site_name))
            with open(filename, "w") as out:
                out.write(format_exc())

            # saving parsing sample
            filename = os.path.join(project_dir, "error-parsing-{}-sample".format(site_name))

            if not isinstance(source, str):  # if sample is not html
                source = obj_dumps(source)
                filename += ".json"

            with open(filename, "w") as out:
                out.write(source)
        raise
    return result


class ParseException(Exception):
    pass


class StructureException(ParseException):
    def __init__(self, msg) -> None:
        super().__init__('structure has changed: {}'.format(msg))


def parse_factor(text):
    return float(text.strip())


def get_text(node):
    return node.text.strip()


def xpath_with_check(node, xpath):
    res = node.xpath(xpath)
    if not res:
        raise ParseException('node not found, xpath: {}'.format(xpath))
    return res


def parse_teams(name, sep):
    teams = name.split(sep)
    if sep not in name:
        raise StructureException('event name')
    if len(teams) != 2:
        return None

    return teams


def contain_part(string, parts, pattern='{}'):
    for part in parts:
        part_pattern = pattern.format(part)
        if search(part_pattern, string):
            return True
    return False


def set_exist_attr(object, name, value):
    getattr(object, name)  # raise AttributeError if attr is not exist
    setattr(object, name, value)
