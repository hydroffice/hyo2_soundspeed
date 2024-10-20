import datetime
import numpy as np
import logging

from hyo2.ssm2.lib.formats.writers.abstract import AbstractTextWriter

logger = logging.getLogger(__name__)


class Hypack(AbstractTextWriter):
    """Hypack writer"""

    def __init__(self):
        super(Hypack, self).__init__()
        self.desc = "Hypack"
        self._ext.add('vel')

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

        # position
        if not self.ssp.cur.meta.latitude or not self.ssp.cur.meta.longitude:
            latitude = 0.0
            longitude = 0.0
        else:
            latitude = self.ssp.cur.meta.latitude
            longitude = self.ssp.cur.meta.longitude
        while longitude > 180.0:
            longitude -= 360.0

        position_string = "{0:.9f} {1:.9f}".format(latitude, longitude)

        # date
        if self.ssp.cur.meta.utc_time:
            date_string = "%s" % self.ssp.cur.meta.utc_time.strftime("%H:%M %m/%d/%Y")
        else:
            date_string = "%s" % datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M %m/%d/%Y")

        header += "FTP NEW 3 " + position_string + " " + date_string + "\r\n"
            
        self.fod.io.write(header)

    def _write_body(self):
        # logger.debug('generating body')
        vi = self.ssp.cur.proc_valid
        for idx in range(np.sum(vi)):
            self.fod.io.write("%.2f %.2f\r\n"
                              % (self.ssp.cur.proc.depth[vi][idx], self.ssp.cur.proc.speed[vi][idx],))
