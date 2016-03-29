from __future__ import absolute_import, division, print_function, unicode_literals

import logging

logger = logging.getLogger(__name__)

from .dicts import Dicts


class Metadata(object):
    def __init__(self):
        self.sensor_type = Dicts.sensor_types['Unknown']
        self.probe_type = Dicts.probe_types['Unknown']
        self.latitude = None
        self.longitude = None
        self.utc_time = None
        self.original_path = None

    def __repr__(self):
        msg = "  <Meta>\n"
        msg += "    <sensor:%s[%s]>\n" % (Dicts.first_match(Dicts.sensor_types, self.sensor_type),
                                          Dicts.first_match(Dicts.probe_types, self.probe_type))
        msg += "    <lat:%s,long:%s>\n" % (self.latitude, self.longitude)
        msg += "    <time:%s>\n" % self.utc_time
        msg += "    <path:%s>\n" % self.original_path
        return msg
