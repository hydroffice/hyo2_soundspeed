from __future__ import absolute_import, division, print_function, unicode_literals

import logging

log = logging.getLogger(__name__)


class Point(object):
    """Used to add a Point type to sqlite"""
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return "(%f;%f)" % (self.x, self.y)


def adapt_point(point):
    return "%f;%f" % (point.x, point.y)


def convert_point(s):
    x, y = map(float, s.split(";"))
    return Point(x, y)
