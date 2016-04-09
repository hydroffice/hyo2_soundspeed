from __future__ import absolute_import, division, print_function, unicode_literals

import os
from datetime import datetime
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
        self._project = None
        self._survey = None
        self._vessel = None
        self._sn = None  # serial number
        self.proc_time = None  # last processing time
        self.proc_info = None  # info about processing

    @property
    def sensor(self):
        return Dicts.first_match(Dicts.sensor_types, self.sensor_type)

    @property
    def probe(self):
        return Dicts.first_match(Dicts.sensor_types, self.sensor_type)

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self.update_proc_time()
        self._project = value

    @property
    def survey(self):
        return self._survey

    @survey.setter
    def survey(self, value):
        self.update_proc_time()
        self._survey = value

    @property
    def vessel(self):
        return self._vessel

    @vessel.setter
    def vessel(self, value):
        self.update_proc_time()
        self._vessel = value

    @property
    def sn(self):
        return self._sn

    @sn.setter
    def sn(self, value):
        self.update_proc_time()
        self._sn = value

    def update_proc_time(self):
        self.proc_time = datetime.utcnow()

    def __repr__(self):
        msg = "  <Meta>\n"
        msg += "    <sensor:%s[%s]>\n" % (self.sensor, self.probe)
        msg += "    <time:%s,lat:%s,long:%s>\n" % (self.latitude, self.longitude, self.utc_time)
        msg += "    <path:%s>\n" % self.original_path
        msg += "    <project:%s,survey:%s,vessel:%s>\n" % (self.project, self.survey, self.vessel)
        msg += "    <sn:%s>\n" % self.sn
        msg += "    <proc_time:%s>\n" % self.proc_time
        msg += "    <proc_info:%s>\n" % self.proc_info
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
        msg += "Last proc. info: %s\n" % self.proc_info
        return msg
