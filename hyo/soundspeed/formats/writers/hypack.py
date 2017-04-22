import numpy as np
import logging

logger = logging.getLogger(__name__)


from hyo.soundspeed.formats.writers.abstract import AbstractTextWriter


class Hypack(AbstractTextWriter):
    """Hypack writer"""

    def __init__(self):
        super(Hypack, self).__init__()
        self.desc = "Hypack"
        self._ext.add('vel')

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

        header += "FTP NEW 2\n"

        self.fod.io.write(header)

    def _write_body(self):
        logger.debug('generating body')
        vi = self.ssp.cur.proc_valid
        for idx in range(np.sum(vi)):
            self.fod.io.write("%.1f %.1f\n"
                              % (self.ssp.cur.proc.depth[vi][idx], self.ssp.cur.proc.speed[vi][idx],))
