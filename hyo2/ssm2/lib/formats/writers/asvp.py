import functools
import logging
import math
import operator
import os

from numpy import sum

# noinspection PyUnresolvedReferences
from hyo2.ssm2 import __version__
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.writers.abstract import AbstractTextWriter
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.profile.dicts import Dicts
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.profile.oceanography import Oceanography as Oc
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.profile.profilelist import ProfileList

logger = logging.getLogger(__name__)


class Asvp(AbstractTextWriter):
    """Kongsberg asvp writer"""

    abs_freqs = [12, 32, 40, 50, 60, 70, 80, 90, 95, 100, 110, 120, 130, 140, 200, 250, 300, 350, 400]

    def __init__(self) -> None:
        super().__init__()
        self.name = "asvp/ssp"
        self.desc = "Kongsberg"
        self._ext.add('asvp')
        self._ext.add('abs')
        self._ext.add('ssp')
        self.header = None  # required for checksum

    def write(self, ssp: ProfileList, data_path: str, data_file: str | None = None, project: str = '') -> bool:
        # logger.debug('*** %s ***: start' % self.driver)

        self.ssp = ssp
        if data_file is None:
            asvp_base_name = os.path.basename(ssp.cur.meta.original_path)
        else:
            asvp_base_name = data_file
        asvp_file = "%s.asvp" % asvp_base_name
        self._write(data_path=data_path, data_file=asvp_file)
        self._write_header()
        self._write_body()
        self.finalize()

        ti = ssp.cur.sis_thinned
        # this part write the absorption files only if the temp and the sal are present
        if (sum(ssp.cur.sis.temp[ti]) != 0) and (sum(ssp.cur.sis.sal[ti]) != 0) \
                and (sum(ssp.cur.sis.speed[ti]) != 0):

            # first write the SSP file
            s01_file = "%s.ssp" % asvp_base_name
            self._write(data_path=data_path, data_file=s01_file)
            self._write_ssp()
            self.finalize()

            # then write all the abs files
            for abs_freq in self.abs_freqs:
                abs_file = "%s_%dkHz.abs" % (asvp_base_name, abs_freq)
                self._write(data_path=data_path, data_file=abs_file)
                self._write_header_abs(abs_freq)
                self._write_body_abs(abs_freq)
                self.finalize()

        else:
            logger.warning("not temperature and/or salinity to create the SSP and the absorption files")

        # logger.debug('*** %s ***: done' % self.driver)
        return True

    def _write_header(self) -> str:
        # logger.debug('generating header')
        header = self._convert_header(fmt=Dicts.kng_formats['ASVP'])
        if self.fod is None:
            raise RuntimeError("FileManager is not set")
        self.fod.io.write(header)
        return header

    def _write_body(self) -> None:
        # logger.debug('generating body')
        body = self._convert_body(fmt=Dicts.kng_formats['ASVP'])
        if self.fod is None:
            raise RuntimeError("FileManager is not set")
        self.fod.io.write(body)

    def _write_ssp(self) -> None:
        ssp = self.ssp
        if ssp is None:
            raise RuntimeError("Profile is not set")
        s01_data = self.convert(ssp, Dicts.kng_formats['S01'])
        if self.fod is None:
            raise RuntimeError("FileManager is not set")
        self.fod.io.write(s01_data)

    def _write_header_abs(self, _):
        # logger.debug('generating header for %d kHz' % freq)
        ssp = self.ssp
        if ssp is None:
            raise RuntimeError("Profile is not set")

        ti = ssp.cur.sis_thinned

        # e.g., ( Absorption  1.0 0 201203212242 22.50000000 -156.50000000 -1 0 0 OMS01_00000 P 0035 )
        abs_header = "( Absorption  1.0 0 "
        abs_header += ssp.cur.meta.utc_time.strftime("%Y%m%d%H%M ")
        abs_header += "%.8f %.8f -1 0 0 SSM_%s P %04d )\n" \
                      % (ssp.cur.meta.latitude,
                         ssp.cur.meta.longitude,
                         __version__,
                         ssp.cur.sis.depth[ti].size)
        if self.fod is None:
            raise RuntimeError("FileManager is not set")
        self.fod.io.write(abs_header)

    def _write_body_abs(self, freq):
        # logger.debug('generating body for %d kHz' % freq)
        ssp = self.ssp
        if ssp is None:
            raise RuntimeError("Profile is not set")

        ti = ssp.cur.sis_thinned

        top_mean = 0
        bottom_mean = 0

        body = str()
        sample_sz = int(sum(ti))
        has_skipped_salinity = False
        for i in range(sample_sz):

            if ssp.cur.sis.sal[ti][i] <= 0:
                if not has_skipped_salinity:
                    logger.info("skipping invalid salinity values")
                    has_skipped_salinity = True
                continue

            abs_value = Oc.attenuation(f=freq, t=ssp.cur.sis.temp[ti][i], d=ssp.cur.sis.depth[ti][i],
                                       s=ssp.cur.sis.sal[ti][i], ph=8.1)

            if i == 0:  # first
                delta = (ssp.cur.sis.depth[ti][0] + ssp.cur.sis.depth[ti][1]) / 2.0

            elif i == sample_sz - 1:  # last
                delta = (ssp.cur.sis.depth[ti][sample_sz - 1] -
                         (ssp.cur.sis.depth[ti][sample_sz - 1] + ssp.cur.sis.depth[ti][sample_sz - 2]) / 2.0)

            else:
                delta = ((ssp.cur.sis.depth[ti][i + 1] + ssp.cur.sis.depth[ti][i]) / 2.0 -
                         (ssp.cur.sis.depth[ti][i] + ssp.cur.sis.depth[ti][i - 1]) / 2.0)

            top_mean += abs_value * delta
            bottom_mean += delta

            mean_abs = top_mean / bottom_mean

            body += "%.3f %.3f %.3f %s\n" \
                    % (ssp.cur.sis.depth[ti][i], abs_value, mean_abs, "999.000")

        if self.fod is None:
            raise RuntimeError("FileManager is not set")
        self.fod.io.write(body)

    def convert(self, ssp: ProfileList, fmt: int) -> str:
        """Convert a profile in a given Kongsberg format"""
        self.ssp = ssp

        header = self._convert_header(fmt)
        body = self._convert_body(fmt)

        return header + body

    def _convert_header(self, fmt: int) -> str:
        ssp = self.ssp
        if ssp is None:
            raise RuntimeError("Profile is not set")
        self.header = self.get_km_prefix(fmt)  # start with the format prefix

        ti = ssp.cur.sis_thinned
        ti_size = ssp.cur.sis.depth[ti].size

        if fmt != Dicts.kng_formats['ASVP']:
            self.header += "%04d," % ti_size
            self.header += ssp.cur.meta.utc_time.strftime("%H%M%S,%d,%m,%Y,")

        else:
            # e.g., ( SoundVelocity  1.0 0 201203212242 22.50000000 -156.50000000 -1 0 0 MVS01_00000 P 0035 )
            self.header += "( SoundVelocity  1.0 0 "
            self.header += ssp.cur.meta.utc_time.strftime("%Y%m%d%H%M ")
            self.header += "%.7f %.7f -1 0 0 SSM_%s P %04d )\n" \
                           % (ssp.cur.meta.latitude,
                              ssp.cur.meta.longitude,
                              __version__,
                              ti_size)
        return self.header

    def _convert_body(self, fmt: int) -> str:
        ssp = self.ssp
        if ssp is None:
            raise RuntimeError("Profile is not set")

        body = str()

        ti = ssp.cur.sis_thinned
        depths = ssp.cur.sis.depth[ti]
        speeds = ssp.cur.sis.speed[ti]
        temps = ssp.cur.sis.temp[ti]
        sals = ssp.cur.sis.sal[ti]

        for i in range(int(sum(ti))):
            if (fmt == Dicts.kng_formats['S00']) or (fmt == Dicts.kng_formats['S10']):
                body += "%.2f,%.1f,,,\r\n" % (depths[i], speeds[i])
            elif (fmt == Dicts.kng_formats['S01']) or (fmt == Dicts.kng_formats['S12']):
                body += "%.2f,%.1f,%.2f,%.2f,\r\n" % (depths[i], speeds[i], temps[i], sals[i])
            elif (fmt == Dicts.kng_formats['S02']) or (fmt == Dicts.kng_formats['S22']):
                body += "%.2f,,%.2f,%.2f,\r\n" % (depths[i], temps[i], sals[i])
            elif fmt == Dicts.kng_formats['ASVP']:
                body += "%.2f %.2f\n" % (depths[i], speeds[i])

        if fmt == Dicts.kng_formats['ASVP']:
            return body

        latitude = ssp.cur.meta.latitude
        if latitude >= 0:
            hem = "N"
        else:
            hem = "S"
        lat_min = int(60 * math.fabs(latitude - int(latitude)))
        lat_decimal_min = int(100 * (60 * math.fabs(latitude - int(latitude)) - lat_min))
        body += "{0:02d}{1:02d}.{2:02d},{3:s},".format(int(math.fabs(latitude)), lat_min, lat_decimal_min, hem)

        longitude = ssp.cur.meta.longitude
        if longitude > 180:  # We need our longitudes to span -180 to 180
            longitude -= 360
        if longitude < 0:
            hem = "W"
        else:
            hem = "E"
        lon_min = int(60 * math.fabs(longitude - int(longitude)))
        lon_decimal_min = int(100 * (60 * math.fabs(longitude - int(longitude)) - lon_min))
        body += "{0:02d}{1:02d}.{2:02d},{3:s},".format(int(math.fabs(longitude)), lon_min, lon_decimal_min, hem)
        body += "0.0,,"
        body += "Source: hyo2.soundspeed,"

        # calculate checksum, XOR of all bytes after the $
        full = self.header + body
        checksum = functools.reduce(operator.xor, map(ord, full[1:len(full)]))
        body += "*{0:02x}".format(checksum)
        body += "\\\r\n"

        return body

    @classmethod
    def get_km_prefix(cls, kng_format: int) -> str:
        """Build output string (PDS2000 requires MV as prefix)"""

        if kng_format == Dicts.kng_formats['S00']:
            output = '$MVS00,00000,'
        elif kng_format == Dicts.kng_formats['S10']:
            output = '$MVS10,00000,'
        elif kng_format == Dicts.kng_formats['S01']:
            output = '$MVS01,00000,'
        elif kng_format == Dicts.kng_formats['S11']:
            output = '$MVS11,00000,'
        elif kng_format == Dicts.kng_formats['S02']:
            output = '$MVS02,00000,'
        elif kng_format == Dicts.kng_formats['S12']:
            output = '$MVS12,00000,'
        elif kng_format == Dicts.kng_formats['ASVP']:
            output = ""
        else:
            raise RuntimeError("unknown kng format: %s" % kng_format)
        return output
