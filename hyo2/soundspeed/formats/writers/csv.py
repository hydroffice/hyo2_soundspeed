import os
import numpy as np
import math
import datetime
import logging

logger = logging.getLogger(__name__)


from hyo2.soundspeed.formats.writers.abstract import AbstractTextWriter


class Csv(AbstractTextWriter):
    """Csv writer"""

    def __init__(self):
        super(Csv, self).__init__()
        self.desc = "CSV"
        self._ext.add('csv')

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

        header = str()

        if self.ssp.cur.meta.utc_time:
            header += "%s" % self.ssp.cur.meta.utc_time.strftime("Date, %Y-%m-%d\n")
            header += "%s" % self.ssp.cur.meta.utc_time.strftime("Time, %H:%M:%S\n")
        else:
            header += "Date, unknown\n"
            header += "Time, unknown\n"

        if self.ssp.cur.meta.latitude and self.ssp.cur.meta.longitude:
            header += "Latitude, %.7f\n" % self.ssp.cur.meta.latitude
            header += "Longitude, %.7f\n" % self.ssp.cur.meta.longitude
        else:
            header += "Latitude, unknown\n"
            header += "Longitude, unknown\n"
        header += "depth (m), sound speed (m/s)\n"

        self.fod.io.write(header)

    def _write_body(self):
        logger.debug('generating body')
        vi = self.ssp.cur.proc_valid
        for idx in range(np.sum(vi)):
            self.fod.io.write("%.2f,%.2f\n"
                              % (self.ssp.cur.proc.depth[vi][idx], self.ssp.cur.proc.speed[vi][idx],))
