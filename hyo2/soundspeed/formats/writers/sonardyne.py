import numpy as np
import logging

logger = logging.getLogger(__name__)

from hyo2.soundspeed import __version__ as ssp_version
from hyo2.soundspeed import __doc__ as ssp_name
from hyo2.soundspeed.formats.writers.abstract import AbstractTextWriter
from hyo2.soundspeed.profile.dicts import Dicts


class Sonardyne(AbstractTextWriter):
    """Sonardyne writer"""

    def __init__(self):
        super(Sonardyne, self).__init__()
        self.desc = "Sonardyne"
        self._ext.add('pro')

    def write(self, ssp, data_path, data_file=None, project=''):
        # logger.debug('*** %s ***: start' % self.driver)

        self._project = project

        self.ssp = ssp
        self._write(data_path=data_path, data_file=data_file)

        self._write_header()
        self._write_body()

        self.finalize()

        # logger.debug('*** %s ***: done' % self.driver)
        return True

    def _write_header(self):
        """Write header: 5 rows -> title, date, time, probe, comments"""
        # logger.debug('generating header')
        header = str()
        # row #0: title
        if self._project:
            header += "%s\n" % self._project
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
        # logger.debug('generating body')
        vi = self.ssp.cur.proc_valid
        for idx in range(np.sum(vi)):
            self.fod.io.write("%12.4f%12.4f%12.4f%12.4f\n"
                              % (self.ssp.cur.proc.depth[vi][idx], self.ssp.cur.proc.speed[vi][idx],
                                 self.ssp.cur.proc.sal[vi][idx], self.ssp.cur.proc.temp[vi][idx]))
