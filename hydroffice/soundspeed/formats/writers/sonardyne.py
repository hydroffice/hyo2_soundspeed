from __future__ import absolute_import, division, print_function, unicode_literals

import logging

logger = logging.getLogger(__name__)

from ... import __version__ as ssp_version
from ... import __doc__ as ssp_name
from .abstract import AbstractTextWriter
from ...profile.dicts import Dicts


class Sonardyne(AbstractTextWriter):
    """Sonardyne writer"""

    def __init__(self):
        super(Sonardyne, self).__init__()
        self._ext.add('pro')

    def write(self, ssp, data_path, data_file=None):
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
        # row #0: title
        if self.ssp.cur.meta.project:
            header += "%s\n" % self.ssp.cur.meta.project
        elif self.ssp.cur.meta.survey:
            header += "%s\n" % self.ssp.cur.meta.survey
        else:
            header += "Generated using HydrOffice %s v.%s\n" % (ssp_name, ssp_version)
        # row #1: date
        if self.ssp.cur.meta.utc_time:
            header += "%s\n" % self.ssp.cur.meta.utc_time.strftime("%d/%m/%Y").lstrip("0").replace("/0", "/")
        else:
            header += "0\n"
        # row #2: time
        if self.ssp.cur.meta.utc_time:
            header += "%s\n" % self.ssp.cur.meta.utc_time.strftime("%H:%M:%S").lstrip("0").replace(":0", ":")
        else:
            header += "0\n"
        # row #3: probe
        if self.ssp.cur.meta.probe_type:
            header += "Probe: %s\n" % Dicts.first_match(Dicts.probe_types, self.ssp.cur.meta.probe_type)
        else:
            header += "0\n"
        # row #4: comments
        if self.ssp.cur.meta.original_path:
            header += "Source: %s\n" % self.ssp.cur.meta.original_path
        else:
            header += "0\n"

        self.fod.io.write(header)

    def _write_body(self):
        logger.debug('generating body')
        for idx in range(self.ssp.cur.data.num_samples):
            self.fod.io.write("%12.4f%12.4f%12.4f%12.4f\n"
                              % (self.ssp.cur.data.depth[idx], self.ssp.cur.data.speed[idx],
                                 self.ssp.cur.data.sal[idx], self.ssp.cur.data.temp[idx]))
