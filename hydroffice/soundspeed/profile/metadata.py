from __future__ import absolute_import, division, print_function, unicode_literals

import os
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
        self.project = None
        self.survey = None
        self.vessel = None
        self.sn = None  # serial number
        self.proc_time = None  # last processing time

    def __repr__(self):
        msg = "  <Meta>\n"
        msg += "    <sensor:%s[%s]>\n" % (Dicts.first_match(Dicts.sensor_types, self.sensor_type),
                                          Dicts.first_match(Dicts.probe_types, self.probe_type))
        msg += "    <time:%s,lat:%s,long:%s>\n" % (self.latitude, self.longitude, self.utc_time)
        msg += "    <path:%s>\n" % self.original_path
        msg += "    <project:%s,survey:%s,vessel:%s>\n" % (self.project, self.survey, self.vessel)
        msg += "    <sn:%s>\n" % self.sn
        msg += "    <proc_time:%s>\n" % self.proc_time
        return msg

    def debug_info(self):
        msg = "Sensor: %s\n" % Dicts.first_match(Dicts.sensor_types, self.sensor_type)
        msg += "Probe: %s\n" % Dicts.first_match(Dicts.probe_types, self.probe_type)
        msg += "Location: %s, %s\n" % (self.latitude, self.longitude)
        msg += "Time: %s\n" % self.utc_time
        if self.original_path:
            msg += "Basename: %s\n" % os.path.basename(self.original_path)
        msg += "Project: %s, Survey: %s, Vessel: %s\n" % (self.project, self.survey, self.vessel)
        msg += "S/N: %s\n" % self.sn
        msg += "Last proc. time: %s\n" % self.proc_time
        return msg
