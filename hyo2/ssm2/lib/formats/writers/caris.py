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

    @classmethod
    def format_caris_dms(cls, coordinate: float, degree_width: int) -> str:
        sign = "-" if coordinate < 0.0 else ""
        total_hundredths = round(abs(coordinate) * 360_000)
        degrees, remainder = divmod(total_hundredths, 360_000)
        minutes, remainder = divmod(remainder, 6_000)
        seconds, hundredths = divmod(remainder, 100)

        return f"{sign}{degrees:0{degree_width}d}:{minutes:02d}:{seconds:02d}.{hundredths:02d}"

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
        latitude = ssp.cur.meta.latitude
        longitude = ssp.cur.meta.longitude

        if latitude is None or longitude is None:
            latitude, longitude = 0.0, 0.0

        if not (math.isfinite(latitude) and math.isfinite(longitude)):
            raise ValueError("CARIS SVP coordinates must be finite.")

        if not -90.0 <= latitude <= 90.0:
            raise ValueError(f"Latitude out of range: {latitude}")

        longitude = math.fmod(longitude, 360.0)
        if longitude > 180.0:
            longitude -= 360.0
        elif longitude < -180.0:
            longitude += 360.0

        latitude_dms = self.format_caris_dms(coordinate=latitude, degree_width=2)
        longitude_dms = self.format_caris_dms(coordinate=longitude, degree_width=3)

        position_string = f"{latitude_dms} {longitude_dms}"

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
