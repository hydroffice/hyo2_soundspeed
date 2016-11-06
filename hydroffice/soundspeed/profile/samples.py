from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import logging

logger = logging.getLogger(__name__)


class Samples(object):
    def __init__(self):
        self.num_samples = 0
        self.pressure = None
        self.depth = None
        self.speed = None
        self.temp = None
        self.conductivity = None
        self.sal = None
        self.source = None
        self.flag = None

    def init_pressure(self):
        self.pressure = np.zeros(self.num_samples)

    def init_depth(self):
        self.depth = np.zeros(self.num_samples)

    def init_speed(self):
        self.speed = np.zeros(self.num_samples)

    def init_temp(self):
        self.temp = np.zeros(self.num_samples)

    def init_conductivity(self):
        self.conductivity = np.zeros(self.num_samples)

    def init_sal(self):
        self.sal = np.zeros(self.num_samples)

    def init_source(self):
        self.source = np.zeros(self.num_samples)

    def init_flag(self):
        self.flag = np.zeros(self.num_samples)

    def resize(self, count):
        """Resize the arrays (if present) to the new given number of elements"""
        if self.num_samples == count:
            return
        self.num_samples = count

        if self.pressure is not None:
            self.pressure.resize(count)
        if self.depth is not None:
            self.depth.resize(count)
        if self.speed is not None:
            self.speed.resize(count)
        if self.temp is not None:
            self.temp.resize(count)
        if self.conductivity is not None:
            self.conductivity.resize(count)
        if self.sal is not None:
            self.sal.resize(count)
        if self.source is not None:
            self.source.resize(count)
        if self.flag is not None:
            self.flag.resize(count)

    def __repr__(self):
        msg = "  <Samples>\n"
        msg += "    <nr:%s>\n" % self.num_samples

        if (self.pressure is not None) and (len(self.pressure) > 2):
            msg += "    <pressure sz:%s min:%.3f max:%.3f>\n" % (self.pressure.shape[0],
                                                                 self.pressure.min(),
                                                                 self.pressure.max())

        if (self.depth is not None) and (len(self.depth) > 2):
            msg += "    <depth sz:%s min:%.3f max:%.3f>\n" % (self.depth.shape[0],
                                                              self.depth.min(),
                                                              self.depth.max())

        if (self.speed is not None) and (len(self.speed) > 2):
            msg += "    <speed sz:%s min:%.3f max:%.3f>\n" % (self.speed.shape[0],
                                                              self.speed.min(),
                                                              self.speed.max())

        if (self.temp is not None) and (len(self.temp) > 2):
            msg += "    <temp sz:%s min:%.3f max:%.3f>\n" % (self.temp.shape[0],
                                                             self.temp.min(),
                                                             self.temp.max())

        if (self.conductivity is not None) and (len(self.conductivity) > 2):
            msg += "    <conductivity sz:%s min:%.3f max:%.3f>\n" % (self.conductivity.shape[0],
                                                                     self.conductivity.min(),
                                                                     self.conductivity.max())

        if (self.sal is not None) and (len(self.sal) > 2):
            msg += "    <sal sz:%s min:%.3f max:%.3f>\n" % (self.sal.shape[0],
                                                            self.sal.min(),
                                                            self.sal.max())

        if (self.source is not None) and (len(self.flag) > 2):
            msg += "    <src sz:%s min:%.3f max:%.3f>\n" % (self.source.shape[0],
                                                            self.source.min(),
                                                            self.source.max())

        if (self.flag is not None) and (len(self.flag) > 2):
            msg += "    <flag sz:%s min:%.3f max:%.3f>\n" % (self.flag.shape[0],
                                                             self.flag.min(),
                                                             self.flag.max())

        return msg
