from __future__ import absolute_import, division, print_function, unicode_literals

import functools
import math
import operator
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)


from hydroffice.soundspeed.formats.writers.abstract import AbstractTextWriter
from hydroffice.soundspeed.profile.dicts import Dicts


class Calc(AbstractTextWriter):
    """AML calc writer"""

    def __init__(self):
        super(Calc, self).__init__()
        self.desc = "aml calc"
        self._ext.add('calc')

    def write(self, ssp, data_path, data_file=None, project=''):
        logger.debug('*** %s ***: start' % self.driver)

        self.ssp = ssp
        self._write(data_path=data_path, data_file=data_file)

        self._write_header()
        self._write_body()

        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _write_header(self):
        logger.debug('generating header')
        header = self._convert_header()
        self.fod.io.write(header)
        return header

    def _write_body(self):
        logger.debug('generating body')
        body = self._convert_body()
        self.fod.io.write(body)

    def convert(self, ssp):
        """Convert a profile in a given Kongsberg format"""
        self.ssp = ssp

        header = self._convert_header()
        body = self._convert_body()

        return header + body

    def _convert_header(self):
        header = str()
        header += self.ssp.cur.meta.utc_time.strftime("CALC,0001,%d-%m-%Y,1,meters\n")
        header += "AML SOUND VELOCITY PROFILER S/N:00000\n"
        header += self.ssp.cur.meta.utc_time.strftime("DATE:%y%j TIME:%H:%M\n")
        header += "DEPTH OFFSET (M):00000.0\n"
        header += "DEPTH (M) VELOCITY (M/S) TEMP (C)\n"
        return header

    def _convert_body(self):
        body = str()
        vi = self.ssp.cur.proc_valid

        last_depth = None
        for i in range(np.sum(vi)):
            if self.ssp.cur.sis.depth[vi][i] < 0.0:
                continue
            body += "%5.1f %4.2f %1.3f\n" % (self.ssp.cur.sis.depth[vi][i],
                                             self.ssp.cur.sis.speed[vi][i],
                                             self.ssp.cur.sis.temp[vi][i])
            last_depth = self.ssp.cur.sis.depth[vi][i]

        body += " 0  0  0\n"
        body += "*** NAV ****\n"
        body += "Bottom Depth (m): %.1f\n" % last_depth
        body += "Ship's Log (N): 0.0\n"

        deg = abs(int(self.ssp.cur.meta.latitude))
        min_value = abs((self.ssp.cur.meta.latitude - deg) * 60.0)
        min_whole = int(min_value)
        min_frac = min_value - min_whole
        if self.ssp.cur.meta.latitude < 0.0:
            hemi = "S"
        else:
            hemi = "N"

        body += "# LAT ( ddmm.mmmmmmm,N): %d%0.2d.%0.7d,%c\n" % (deg, min_whole, min_frac, hemi)

        # LON (dddmm.mmmmmmm,N):  4105.3385200,N
        deg = abs(int(self.ssp.cur.meta.longitude))
        min_value = abs((abs(self.ssp.cur.meta.longitude) - deg) * 60.0)
        if deg > 180:
            deg -= 360
        min_whole = int(min_value)
        min_frac = min_value - min_whole
        if self.ssp.cur.meta.longitude < 0.0:
            hemi = "W"
        else:
            hemi = "E"

        # logger.debug("Lon: %s" % (self.longitude, deg, min_value, min_whole, min_frac, hemi))

        body += "# LON (dddmm.mmmmmmm,N): %d%0.2d.%0.7d,%c\n" % (deg, min_whole, min_frac, hemi)

        body += self.ssp.cur.meta.utc_time.strftime("Time [hh:mm:ss.ss]: %H:%M:%S.00\n")
        body += self.ssp.cur.meta.utc_time.strftime("Date [dd/mm/yyyy]: %d:%m:%Y\n")

        return body
