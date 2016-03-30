from __future__ import absolute_import, division, print_function, unicode_literals

import netCDF4
import datetime as dt
import numpy as np
import logging

logger = logging.getLogger(__name__)


from ..abstract import AbstractBinaryReader
from ...profile.dicts import Dicts
from ...helper import FileInfo


class Turo(AbstractBinaryReader):
    """Turo reader -> XBT style

    Info: http://www.turo.com.au/
    """

    def __init__(self):
        super(Turo, self).__init__()
        self._ext.add('nc')

    def read(self, data_path):
        logger.debug('*** %s ***: start' % self.driver)

        self.init_data()  # create a new empty profile

        # initialize probe/sensor type
        self.ssp.meta.sensor_type = Dicts.sensor_types['XBT']
        self.ssp.meta.probe_type = Dicts.probe_types['XBT']

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _read(self, data_path):
        """Helper function to read the raw file"""
        self.fid = FileInfo(data_path)
        self.fid.io = netCDF4.Dataset(self.fid.path)

    def _parse_header(self):
        """Parsing header: time, latitude, longitude"""
        logger.debug('parsing header')

        date = str(self.fid.io.variables['woce_date'][0])
        time = "%.6d" % self.fid.io.variables['woce_time'][0]  # forcing leading zeros for hh
        self.ssp.meta.utc_time = dt.datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]),
                                            int(time[0:2]), int(time[2:4]), int(time[4:6]), 0)

        self.ssp.meta.latitude = self.fid.io.variables['latitude'][0]
        self.ssp.meta.longitude = self.fid.io.variables['longitude'][0]

        if not self.ssp.meta.original_path:
            self.ssp.meta.original_path = self.fid.path

    def _parse_body(self):
        """Parsing samples: depth, speed, temp, sal"""
        logger.debug('parsing body')

        self.ssp.data.depth = self.fid.io.variables['depth'][:]
        self.ssp.data.speed = self.fid.io.variables['soundSpeed'][0, :, 0, 0]
        self.ssp.data.temp = self.fid.io.variables['temperature'][0, :, 0, 0]
        self.num_samples = self.ssp.data.depth.size
        self.ssp.data.sal = np.zeros(self.num_samples)

        self.fid.io.close()
