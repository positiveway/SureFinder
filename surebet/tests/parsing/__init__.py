import os

package_dir = os.path.dirname(__file__)


def read_html(filename) -> str:
    with open(filename, encoding='utf8') as file:
        return file.read()
