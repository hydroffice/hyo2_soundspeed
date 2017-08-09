import numpy as np
import math
import datetime
import logging

logger = logging.getLogger(__name__)


from hyo.soundspeed.formats.writers.abstract import AbstractTextWriter


class Caris(AbstractTextWriter):
    """CARIS svp writer"""

    def __init__(self):
        super(Caris, self).__init__()
        self.desc = "CARIS"
        self._ext.add('svp')

    def write(self, ssp, data_path, data_file=None, project=''):
        logger.debug('*** %s ***: start' % self.driver)

        self._project = project
        self.ssp = ssp
        if data_file is None:
            data_file = self._project
        self._write(data_path=data_path, data_file=data_file, append=True)

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

        abs_lat = math.fabs(latitude)
        lat_min = int(60 * (abs_lat - int(abs_lat)))
        lat_sec = 3600 * (abs_lat - int(abs_lat) - lat_min / 60.0)
        abs_lon = math.fabs(longitude)
        lon_min = int(60 * (abs_lon - int(abs_lon)))
        lon_sec = 3600 * (abs_lon - int(abs_lon) - lon_min / 60.0)

        position_string = "{0:02d}:{1:02d}:{2:05.2f} {3:02d}:{4:02d}:{5:05.2f}".format(int(latitude),
                                                                                       lat_min, lat_sec,
                                                                                       int(longitude),
                                                                                       lon_min, lon_sec)

        header += "Section " + date_string + " " + position_string + " Created by hyo.soundspeed\n"
        self.fod.io.write(header)

    def _write_body(self):
        logger.debug('generating body')
        vi = self.ssp.cur.proc_valid
        for idx in range(np.sum(vi)):
            self.fod.io.write("%.6f %.6f\n"
                              % (self.ssp.cur.proc.depth[vi][idx], self.ssp.cur.proc.speed[vi][idx],))
