from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import struct
import calendar
import logging

logger = logging.getLogger(__name__)

from .abstract import AbstractTextWriter
from ...profile.dicts import Dicts


class Qps(AbstractTextWriter):
    """QPS bsvp writer"""

    def __init__(self):
        super(Qps, self).__init__()
        self.desc = "QPS"
        self._ext.add('bsvp')

    def write(self, ssp, data_path, data_file=None, data_append=False, project=''):
        logger.debug('*** %s ***: start' % self.driver)

        self.ssp = ssp
        self._write(data_path=data_path, data_file=data_file, append=data_append, encoding=None, binary=True)

        self._write_header()
        self._write_body()

        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _write_header(self):
        logger.debug('generating header')

        vi = self.ssp.cur.proc_valid
        epoch = int(calendar.timegm(self.ssp.cur.meta.utc_time.timetuple()))
        header = struct.pack('dddi', epoch, self.ssp.cur.meta.latitude, self.ssp.cur.meta.longitude, np.sum(vi))
        # header = '%s %.7f %.7f %i\n' % (epoch, self.ssp.cur.meta.latitude, self.ssp.cur.meta.longitude, np.sum(vi))
        self.fod.io.write(header)

    def _write_body(self):
        """ source and quality flags
        // Bit 0-7 - Source
        // 0x01 = Observed
        // 0x02 = Oceanographic Model
        // 0x04 = User designated
        // Bit 8-15 - Quality
        // 0x01 = Generic Bad
        // Bit 16-23 - Editing
        // 0x01 = Deleted
        // 0x02 = Added (by user)
        """
        logger.debug('generating body')
        if self.ssp.cur.meta.sensor_type != Dicts.sensor_types['Unknown'] and \
                self.ssp.cur.meta.sensor_type != Dicts.sensor_types['Synthetic']:
            _flags = 2**0 # Observed
        elif self.ssp.cur.meta.probe_type == Dicts.probe_types['RTOFS']:
            _flags = 2**1 # Oceanographic Model
        else:
            _flags = 2**2 # User designated
        vi = self.ssp.cur.proc_valid
        for idx in range(np.sum(vi)):
            depth = self.ssp.cur.proc.depth[vi][idx]
            speed = self.ssp.cur.proc.speed[vi][idx]
            temperature = self.ssp.cur.proc.temp[vi][idx]
            salinity = self.ssp.cur.proc.sal[vi][idx]
            pressure = self.ssp.cur.proc.pressure[vi][idx]
            conductivity = self.ssp.cur.proc.conductivity[vi][idx]
            source = self.ssp.cur.proc.source[vi][idx]
            if source == Dicts.sources['raw']:
                flags = _flags
            elif source == Dicts.sources['user']:
                flags = 2**2 + 2**17 # User designated and Added (by user)
            elif source == Dicts.sources['rtofs_ext']:
                flags = 2**1 # Oceanographic Model
            else:
                flags = 2**2 # User designated
                
            data = struct.pack('iffffffI', idx, depth, speed, temperature, salinity, pressure, conductivity, flags)
            # data = '%i %.1f %.1f %.1f %.1f %.1f %.1f %i\n' % (idx, depth, speed, temperature, salinity, pressure, conductivity, flags)
            self.fod.io.write(data)
