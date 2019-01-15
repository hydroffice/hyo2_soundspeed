import netCDF4
import datetime as dt
import numpy as np
import logging

logger = logging.getLogger(__name__)

from hyo2.soundspeed.formats.readers.abstract import AbstractBinaryReader
from hyo2.soundspeed.base.files import FileInfo
from hyo2.soundspeed.profile.dicts import Dicts
from hyo2.soundspeed.base.callbacks.cli_callbacks import CliCallbacks


class Turo(AbstractBinaryReader):
    """Turo reader -> XBT style

    Info: http://www.turo.com.au/
    """

    def __init__(self):
        super(Turo, self).__init__()
        self.desc = "Turo"
        self._ext.add('nc')

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize probe/sensor type
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['XBT']
        self.ssp.cur.meta.probe_type = Dicts.probe_types['XBT']

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.fix()
        if self.ssp.cur.data.sal.mean() == 0:  # future use
            self.ssp.cur.calc_salinity()
        self.finalize()

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
        self.ssp.cur.meta.utc_time = dt.datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]),
                                                 int(time[0:2]), int(time[2:4]), int(time[4:6]), 0)

        self.ssp.cur.meta.latitude = self.fid.io.variables['latitude'][0]
        self.ssp.cur.meta.longitude = self.fid.io.variables['longitude'][0]

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

    def _parse_body(self):
        """Parsing samples: depth, speed, temp, sal"""
        logger.debug('parsing body')

        depth = self.fid.io.variables['depth'][:]
        try:
            speed = self.fid.io.variables['soundSpeed'][0, :, 0, 0]
        except KeyError:
            try:
                speed = self.fid.io.variables['derivedSoundSpeed'][0, :, 0, 0]
            except KeyError:
                logger.info("missing sound speed")
                self.missing_sound_speed = True
                speed = np.zeros(depth.size)
        temp = self.fid.io.variables['temperature'][0, :, 0, 0]
        self.ssp.cur.init_data(depth.size)

        self.fid.io.close()

        count = 0
        for i in range(self.ssp.cur.data.num_samples):
            # Skipping invalid data (crazy sound speed)
            if isinstance(speed[i], np.ma.core.MaskedConstant):
                continue

            self.ssp.cur.data.depth[count] = depth[i]
            self.ssp.cur.data.temp[count] = temp[i]
            self.ssp.cur.data.speed[count] = speed[i]
            count += 1

        self.ssp.cur.data_resize(count)
