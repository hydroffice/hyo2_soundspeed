from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import os
import logging

logger = logging.getLogger(__name__)


from hydroffice.soundspeed.formats.writers.abstract import AbstractTextWriter
from hydroffice.soundspeed.profile.oceanography import Oceanography as Oc


class Elac(AbstractTextWriter):
    """ELAC writer"""

    def __init__(self):
        super(Elac, self).__init__()
        self.desc = "ELAC"
        self._ext.add('sva')

    def write(self, ssp, data_path, data_file=None, project=''):
        """Writing version 2 since it holds T/S and flags"""
        logger.debug('*** %s ***: start' % self.driver)

        self.ssp = ssp
        self._write(data_path=data_path, data_file=data_file)

        self._write_header()
        self._write_body()

        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _write_header(self):
        """Write header: 5 rows -> title, date, time, probe, comments"""
        logger.debug('generating header')
        header = "# depth   veloc.    temp.     salin.    cond.\n" \
                 "# [m]     [m/s]     [?C]      [o/oo]    [mmho/cm]\n" \
                 "\n" \
                 ".profile 0\n"

        self.fod.io.write(header)

    def _write_body(self):
        logger.debug('generating body')
        vi = self.ssp.cur.proc_valid
        for idx in range(np.sum(vi)):
            self.fod.io.write("%8.2f%10.2f%10.2f%10.2f%10.2f\n"
                              % (self.ssp.cur.proc.depth[vi][idx], self.ssp.cur.proc.speed[vi][idx],
                                 self.ssp.cur.proc.temp[vi][idx], self.ssp.cur.proc.sal[vi][idx],
                                 Oc.s2c(s=self.ssp.cur.proc.sal[vi][idx],
                                        p=Oc.d2p(d=self.ssp.cur.proc.depth[vi][idx],
                                                 lat=self.ssp.cur.meta.latitude),
                                        t=self.ssp.cur.proc.temp[vi][idx])))
