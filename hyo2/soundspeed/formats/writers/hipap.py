import numpy as np
import logging

from hyo2.soundspeed.formats.writers.abstract import AbstractTextWriter

logger = logging.getLogger(__name__)


class Hipap(AbstractTextWriter):
    """Hypack writer"""

    def __init__(self):
        super(Hipap, self).__init__()
        self.desc = "HiPAP"
        self._ext.add('USR')

    def write(self, ssp, data_path, data_file=None, project=''):
        # logger.debug('*** %s ***: start' % self.driver)

        self.ssp = ssp
        self._write(data_path=data_path, data_file=data_file)

        self._write_header()
        self._write_body()

        self.finalize()

        # logger.debug('*** %s ***: done' % self.driver)
        return True

    def _write_header(self):
        # logger.debug('generating header')

        header = str()

        header += "SSP Cast on %s %s,\n" % \
                  (self.ssp.cur.meta.utc_time.strftime("%d/%m/%Y").lstrip("0").replace("/0", "/"),
                   self.ssp.cur.meta.utc_time.strftime("%H:%M:%S").lstrip("0").replace(":0", ":"))

        self.fod.io.write(header)

    def _write_body(self):
        # logger.debug('generating body')
        vi = self.ssp.cur.proc_valid
        for idx in range(np.sum(vi)):
            self.fod.io.write("%.1f,%.1f\n"
                              % (self.ssp.cur.proc.depth[vi][idx], self.ssp.cur.proc.speed[vi][idx],))
