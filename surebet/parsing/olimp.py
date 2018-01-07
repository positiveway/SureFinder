import lxml.html


def parse(source):
    html = lxml.html.fromstring(source)
