from __future__ import absolute_import, division, print_function, unicode_literals

import logging

logger = logging.getLogger(__name__)

from ... import __version__ as ssp_version
from ... import __doc__ as ssp_name
from ..abstract import AbstractTextWriter
from ...profile.dicts import Dicts


class Unb(AbstractTextWriter):
    """UNB writer"""

    def __init__(self):
        super(Unb, self).__init__()
        self._ext.add('unb')

    def write(self, ssp, data_path, data_file=None):
        """Writing version 2 since it holds T/S and flags"""
        logger.debug('*** %s ***: start' % self.driver)

        self.ssp = ssp
        self._write(data_path=data_path, data_file=data_file)

        self._write_header()
        self._write_body()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _write_header(self):
        """Write header: 5 rows -> title, date, time, probe, comments"""
        logger.debug('generating header')
        header = str()
        # row #0: version
        header += "2  # Generated using HydrOffice %s v.%s\n" % (ssp_name, ssp_version)
        # row #1: date and time of observation
        if self.ssp.meta.utc_time:
            header += "%s # date and time of observation\n" % self.ssp.meta.utc_time.strftime("%Y %j %H:%M:%S")
        else:
            header += "0000 000 00:00:00 # date and time of observation\n"
        # row #2: date and time of logging (when inserted into MB logging stream)
        header += "0000 000 00:00:00 # date and time of logging (when inserted into MB logging stream)\n"
        # row #3: lat and long of observation
        if self.ssp.meta.latitude and self.ssp.meta.longitude:
            header += "%.6f %.6f # lat and long of observation\n" % (self.ssp.meta.latitude, self.ssp.meta.longitude)
        else:
            header += "0.000000 0.000000 # lat and long of observation\n"
        # row #4: lat and long of ship when inserted
        header += "0.000000 0.000000 # lat and long of ship when inserted\n"
        # row #5: no. of raw observations
        header += "%d # no. of raw observations\n" % self.ssp.data.num_samples
        # rows #6-15: blanck
        header += "# blank line for future parameter 1 of 10\n" \
                  "# blank line for future parameter 2 of 10\n" \
                  "# blank line for future parameter 3 of 10\n" \
                  "# blank line for future parameter 4 of 10\n" \
                  "# blank line for future parameter 5 of 10\n" \
                  "# blank line for future parameter 6 of 10\n" \
                  "# blank line for future parameter 7 of 10\n" \
                  "# blank line for future parameter 8 of 10\n" \
                  "# blank line for future parameter 9 of 10\n" \
                  "# blank line for future parameter 10 of 10\n"

        self.fod.io.write(header)

    def _write_body(self):
        logger.debug('generating body')
        for idx in range(self.ssp.data.num_samples):
            self.fod.io.write("%d %.3f %.3f %.3f %.3f 0.000 0\n"
                              % (idx+1, self.ssp.data.depth[idx], self.ssp.data.speed[idx],
                                 self.ssp.data.temp[idx], self.ssp.data.sal[idx]))
