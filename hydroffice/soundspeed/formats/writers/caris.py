from __future__ import absolute_import, division, print_function, unicode_literals

import os
import numpy as np
import math
import datetime
import logging

logger = logging.getLogger(__name__)


from .abstract import AbstractTextWriter


class Caris(AbstractTextWriter):
    """Caris svp writer"""

    def __init__(self):
        super(Caris, self).__init__()
        self.desc = "Caris"
        self._ext.add('svp')

    def write(self, ssp, data_path, data_file=None, data_append=False, project=''):
        logger.debug('*** %s ***: start' % self.driver)

        self.ssp = ssp
        self._write(data_path=data_path, data_file=data_file, append=data_append)

        self._write_header()
        self._write_body()

        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _write_header(self):
        logger.debug('generating header')

        header = str()

        logger.debug("append: %s" % self.fod.append_exists)
        if not self.fod.append_exists:
            header += "[SVP_VERSION_2]\n"
            header += "%s\n" % self.fod.path

        # date
        if self.ssp.cur.meta.utc_time:
            date_string = "%s" % self.ssp.cur.meta.utc_time.strftime("%Y-%j %H:%M:%S")
        else:
            date_string = "%s" % datetime.datetime.now().strftime("%Y-%j %H:%M:%S")

        # position
        if not self.ssp.cur.meta.latitude or not self.ssp.cur.meta.longitude:
            latitude = 0.0
            longitude = 0.0
        else:
            latitude = self.ssp.cur.meta.latitude
            longitude = self.ssp.cur.meta.longitude
        while longitude > 180.0:
            longitude -= 360.0
        lat_min = int(60 * math.fabs(latitude - int(latitude)))
        lat_sec = 60 * int(100 * (60 * math.fabs(latitude - int(latitude)) - lat_min))
        lon_min = int(60 * math.fabs(longitude - int(longitude)))
        lon_sec = 60 * int(100 * (60 * math.fabs(longitude - int(longitude)) - lon_min))
        position_string = "{0:02d}:{1:02d}:{2:05.2f} {3:02d}:{4:02d}:{2:05.2f}".format(int(latitude),
                                                                                       lat_min, lat_sec,
                                                                                       int(longitude),
                                                                                       lon_min, lon_sec)
        header += "Section " + date_string + " " + position_string + " Created by hydroffice.soundspeed\n"
        self.fod.io.write(header)

    def _write_body(self):
        logger.debug('generating body')
        vi = self.ssp.cur.proc_valid
        for idx in range(np.sum(vi)):
            self.fod.io.write("%.6f %.6f\n"
                              % (self.ssp.cur.proc.depth[vi][idx], self.ssp.cur.proc.speed[vi][idx],))
