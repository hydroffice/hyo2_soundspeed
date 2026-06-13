import datetime
import logging
import math

from numpy import sum

# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.abstract import AbstractTextWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.profile.profilelist import ProfileList

logger = logging.getLogger(__name__)


class Caris(AbstractTextWriter):
    """CARIS svp writer"""

    def __init__(self) -> None:
        super(Caris, self).__init__()
        self.desc = "CARIS"
        self._ext.add('svp')

    def write(self, ssp: ProfileList, data_path: str, data_file: str | None = None, project: str = '') -> bool:
        # logger.debug('*** %s ***: start' % self.driver)

        self._project = project
        self.ssp = ssp
        if data_file is None:
            data_file = self._project
        self._write(data_path=data_path, data_file=data_file, append=True)

        self._write_header()
        self._write_body()

        self.finalize()

        # logger.debug('*** %s ***: done' % self.driver)
        return True

    def _write_header(self) -> str:
        if self.fod is None:
            raise RuntimeError("FileManager is not set")
        ssp = self.ssp
        if ssp is None:
            raise RuntimeError("Profile is not set")

        header = str()

        logger.debug("append: %s" % self.fod.append_exists)
        if not self.fod.append_exists:
            header += "[SVP_VERSION_2]\r\n"
            header += "%s\r\n" % self.fod.path

        # date
        if ssp.cur.meta.utc_time:
            date_string = "%s" % ssp.cur.meta.utc_time.strftime("%Y-%j %H:%M:%S")
        else:
            date_string = "%s" % datetime.datetime.now().strftime("%Y-%j %H:%M:%S")

        # position
        if not ssp.cur.meta.latitude or not ssp.cur.meta.longitude:
            latitude = 0.0
            longitude = 0.0
        else:
            latitude = ssp.cur.meta.latitude
            longitude = ssp.cur.meta.longitude
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

        header += "Section " + date_string + " " + position_string + "\r\n"
        self.fod.io.write(header)
        return header

    def _write_body(self) -> None:
        if self.fod is None:
            raise RuntimeError("FileManager is not set")
        ssp = self.ssp
        if ssp is None:
            raise RuntimeError("Profile is not set")

        vi = ssp.cur.proc_valid
        # noinspection PyTypeChecker
        for idx in range(sum(vi)):
            self.fod.io.write("%.6f %.6f\r\n"
                              % (ssp.cur.proc.depth[vi][idx], ssp.cur.proc.speed[vi][idx],))
