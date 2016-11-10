from __future__ import absolute_import, division, print_function, unicode_literals

import os
import numpy as np
import math
import datetime
import logging

logger = logging.getLogger(__name__)


from .abstract import AbstractTextWriter


class Ixblue(AbstractTextWriter):
    """Ixblue writer"""

    def __init__(self):
        super(Ixblue, self).__init__()
        self.desc = "Ixblue"
        self._ext.add('txt')

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

    def _write_body(self):
        logger.debug('generating body')
        vi = self.ssp.cur.proc_valid
        for idx in range(np.sum(vi)):
            self.fod.io.write("%.2f %.2f\n"
                              % (self.ssp.cur.proc.depth[vi][idx], self.ssp.cur.proc.speed[vi][idx],))
