from __future__ import absolute_import, division, print_function, unicode_literals

import functools
import math
import operator
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)


from .abstract import AbstractTextWriter
from ...profile.dicts import Dicts


class Asvp(AbstractTextWriter):
    """Kongsberg asvp writer"""

    def __init__(self):
        super(Asvp, self).__init__()
        self.desc = "Konsgberg asvp"
        self._ext.add('asvp')
        self.header = None  # required for checksum

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
        header = self._convert_header(fmt=Dicts.kng_formats['ASVP'])
        self.fod.io.write(header)
        return header

    def _write_body(self):
        logger.debug('generating body')
        body = self._convert_body(fmt=Dicts.kng_formats['ASVP'])
        self.fod.io.write(body)

    def convert(self, ssp, fmt):
        """Convert a profile in a given Kongsberg format"""
        self.ssp = ssp

        header = self._convert_header(fmt)
        body = self._convert_body(fmt)

        return header + body

    def _convert_header(self, fmt):
        self.header = self.get_km_prefix(fmt)  # start with the format prefix
        ti = self.ssp.cur.sis_thinned

        if fmt != Dicts.kng_formats['ASVP']:
            self.header += "%04d," % self.ssp.cur.sis.depth[ti].size
            self.header += self.ssp.cur.meta.utc_time.strftime("%H%M%S,%d,%m,%Y,")

        else:
            # e.g., ( SoundVelocity  1.0 0 201203212242 22.50000000 -156.50000000 -1 0 0 MVS01_00000 P 0035 )
            self.header += "( SoundVelocity  1.0 0 "
            self.header += self.ssp.cur.meta.utc_time.strftime("%Y%m%d%H%M%S ")
            self.header += "%.7f %.7f -1 0 0 OMS01_00000 P %4d )\n" \
                           % (self.ssp.cur.meta.latitude,
                              self.ssp.cur.meta.longitude,
                              self.ssp.cur.sis.depth[ti].size)
        return self.header

    def _convert_body(self, fmt):
        body = str()
        ti = self.ssp.cur.sis_thinned

        for i in range(np.sum(ti)):
            if (fmt == Dicts.kng_formats['S00']) or (fmt == Dicts.kng_formats['S10']):
                body += "%.2f,%.1f,,,\r\n" \
                        % (self.ssp.cur.sis.depth[ti][i], self.ssp.cur.sis.speed[ti][i])
            elif (fmt == Dicts.kng_formats['S01']) or (fmt == Dicts.kng_formats['S12']):
                body += "%.2f,%1f,%.2f,%.2f,\r\n" \
                        % (self.ssp.cur.sis.depth[ti][i], self.ssp.cur.sis.speed[ti][i],
                           self.ssp.cur.sis.temp[ti][i], self.ssp.cur.sis.sal[ti][i])
            elif (fmt == Dicts.kng_formats['S02']) or (fmt == Dicts.kng_formats['S22']):
                body += "%.2f,,%.2f,%.2f,\r\n" \
                        % (self.ssp.cur.sis.depth[ti][i],
                           self.ssp.cur.sis.temp[ti][i], self.ssp.cur.sis.sal[ti][i])
            elif fmt == Dicts.kng_formats['ASVP']:
                body += "%.2f %.1f\n" \
                        % (self.ssp.cur.sis.depth[ti][i], self.ssp.cur.sis.speed[ti][i])

        if fmt == Dicts.kng_formats['ASVP']:
            return body

        latitude = self.ssp.cur.meta.latitude
        if latitude >= 0:
            hem = "N"
        else:
            hem = "S"
        lat_min = int(60 * math.fabs(latitude - int(latitude)))
        lat_decimal_min = int(100 * (60 * math.fabs(latitude - int(latitude)) - lat_min))
        body += "{0:02d}{1:02d}.{2:02d},{3:s},".format(int(math.fabs(latitude)), lat_min, lat_decimal_min, hem)

        longitude = self.ssp.cur.meta.longitude
        if longitude > 180:  # We need our longitudes to span -180 to 180
            longitude -= 360
        if longitude < 0:
            hem = "W"
        else:
            hem = "E"
        lon_min = int(60 * math.fabs(longitude - int(longitude)))
        lon_decimal_min = int(100 * (60 * math.fabs(longitude - int(longitude)) - lon_min))
        body += "{0:02d}{1:02d}.{2:02d},{3:s},".format(int(math.fabs(longitude)), lon_min, lon_decimal_min, hem)
        body += "0.0,"
        body += "Source: hydroffice.soundspeed,"

        # calculate checksum, XOR of all bytes after the $
        full = self.header + body
        checksum = functools.reduce(operator.xor, map(ord, full[1:len(full)]))
        body += "*{0:02x}".format(checksum)
        body += "\\\r\n"

        return body

    @classmethod
    def get_km_prefix(cls, kng_format):
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
