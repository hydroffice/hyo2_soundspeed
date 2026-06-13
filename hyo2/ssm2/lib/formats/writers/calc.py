import logging

from numpy import sum

# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.abstract import AbstractTextWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.profile.profilelist import ProfileList

logger = logging.getLogger(__name__)


class Calc(AbstractTextWriter):
    """AML calc writer"""

    def __init__(self) -> None:
        super().__init__()
        self.desc = "CALC"
        self._ext.add('calc')

    def write(self, ssp: ProfileList, data_path: str, data_file: str | None = None, project: str = '') -> bool:
        logger.debug('*** %s ***: start' % self.driver)

        self.ssp = ssp
        self._write(data_path=data_path, data_file=data_file)

        self._write_header()
        self._write_body()

        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _write_header(self) -> str:
        if self.fod is None:
            raise RuntimeError("FileManager is not set")

        logger.debug('generating header')
        header = self._convert_header()
        self.fod.io.write(header)
        return header

    def _write_body(self) -> None:
        if self.fod is None:
            raise RuntimeError("FileManager is not set")

        logger.debug('generating body')
        body = self._convert_body()
        self.fod.io.write(body)

    def convert(self, ssp: ProfileList, for_hypack: bool = False) -> str:
        """Convert a profile in AML Oceanographic Calc format"""
        self.ssp = ssp

        header = self._convert_header()
        body = self._convert_body(hypack=for_hypack)

        return header + body

    def _convert_header(self) -> str:
        ssp = self.ssp
        if ssp is None:
            raise RuntimeError("Profile is not set")

        header = str()
        header += ssp.cur.meta.utc_time.strftime("CALC,0001,%d-%m-%Y,1,meters\n")
        header += "AML SOUND VELOCITY PROFILER S/N:00000\n"
        header += ssp.cur.meta.utc_time.strftime("DATE:%y%j TIME:%H:%M\n")
        header += "DEPTH OFFSET (M):00000.0\n"
        header += "DEPTH (M) VELOCITY (M/S) TEMP (C)\n"
        return header

    def _convert_body(self, hypack: bool = False) -> str:
        ssp = self.ssp
        if ssp is None:
            raise RuntimeError("Profile is not set")
        body = str()
        vi = ssp.cur.proc_valid

        last_depth = None
        for i in range(sum(vi)):
            if hypack:
                # Hypack supports two decimal precision for depth, which differs from
                # the one decimal precision of the AML Calc format. Also, Hypack has
                # showcased erratic behavior when receiving depth values of 0.00m.

                if ssp.cur.proc.depth[vi][i] < 0.01:
                    continue
                body += "%7.2f %8.2f %7.3f\n" % (ssp.cur.proc.depth[vi][i],
                                                 ssp.cur.proc.speed[vi][i],
                                                 ssp.cur.proc.temp[vi][i])
            else:
                if ssp.cur.proc.depth[vi][i] < 0.0:
                    continue
                body += "%7.1f %8.2f %7.3f\n" % (ssp.cur.proc.depth[vi][i],
                                                 ssp.cur.proc.speed[vi][i],
                                                 ssp.cur.proc.temp[vi][i])
            last_depth = ssp.cur.proc.depth[vi][i]

        body += "0  0  0\n"
        body += "*** NAV ****\n"
        body += "Bottom Depth (m): %s\n" % last_depth
        body += "Ship's Log (N): 0.0\n"

        # LAT (ddmm.mmmmmmm,N):  4105.3385200,N
        deg = abs(int(ssp.cur.meta.latitude))
        min_value = abs((ssp.cur.meta.latitude - deg) * 60.0)
        if ssp.cur.meta.latitude < 0.0:
            hemi = "S"
        else:
            hemi = "N"

        body += "# LAT ( ddmm.mmmmmmm,N): %02d%010.7f,%c\n" % (deg, min_value, hemi)

        # LON (dddmm.mmmmmmm,W):  07028.7334500,W
        deg = abs(int(ssp.cur.meta.longitude))
        min_value = abs((abs(ssp.cur.meta.longitude) - deg) * 60.0)
        if deg > 180:
            deg -= 360
        if ssp.cur.meta.longitude < 0.0:
            hemi = "W"
        else:
            hemi = "E"

        body += "# LON (dddmm.mmmmmmm,E): %03d%010.7f,%c\n" % (deg, min_value, hemi)

        body += ssp.cur.meta.utc_time.strftime("Time [hh:mm:ss.ss]: %H:%M:%S.00\n")
        body += ssp.cur.meta.utc_time.strftime("Date [dd/mm/yyyy]: %d/%m/%Y\n")

        return body
