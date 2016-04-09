from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt
import logging

logger = logging.getLogger(__name__)


from .abstract import AbstractTextReader
from ...profile.dicts import Dicts
from ...base.callbacks import Callbacks


class Unb(AbstractTextReader):
    """UNB reader"""

    def __init__(self):
        super(Unb, self).__init__()
        self.desc = "UNB"
        self._ext.add('unb')

        self.version = None  # Only version 2 and higher holds T/S and flags

    def read(self, data_path, settings, callbacks=Callbacks()):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.version = None

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize probe/sensor type
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['XBT']  # faking XBT
        self.ssp.cur.meta.probe_type = Dicts.probe_types['XBT']

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        logger.debug('parsing header')
        try:  # version
            self.version = int(self.lines[0].split()[0])
            logger.info("version: %s" % self.version)
        except ValueError:
            logger.warning("unable to parse the version from line #%s" % self.samples_offset)

        try:  # time
            self.samples_offset = 1
            year = int(self.lines[1].split()[0])
            jday = int(self.lines[1].split()[1])
            time = self.lines[1].split()[2]
            hour, minute, second = [int(i) for i in time.split(':')]
            self.ssp.cur.meta.utc_time = dt.datetime(year, 1, 1, hour, minute, second) + dt.timedelta(days=jday-1)
        except ValueError:
            logger.warning("unable to parse the time from line #%s" % self.samples_offset)

        try:  # latitude and longitude
            self.samples_offset = 3
            self.ssp.cur.meta.latitude = float(self.lines[3].split()[0])
            self.ssp.cur.meta.longitude = float(self.lines[3].split()[1])
        except ValueError:
            logger.warning("unable to parse the position from line #%s" % self.samples_offset)

        num_samples = 0
        try:  # num samples
            self.samples_offset = 3
            num_samples = int(self.lines[5].split()[0])
        except ValueError:
            logger.warning("unable to parse the number of samples from line #%s" % self.samples_offset)

        self.samples_offset = 16

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample structures
        self.ssp.cur.init_data(num_samples)
        # initialize additional fields
        self.more_fields.append('Depth')
        self.more_fields.append('Flag')
        self.ssp.cur.init_more(self.more_fields)

    def _parse_body(self):
        """Parsing samples: depth, speed, temp, sal"""
        logger.debug('parsing body')

        count = 0
        for line in self.lines[self.samples_offset:len(self.lines)]:

            # skip empty lines
            if len(line.split()) == 0:
                continue

            data = line.split()
            # first required data fields
            try:
                self.ssp.cur.data.depth[count] = float(data[1])
                self.ssp.cur.data.speed[count] = float(data[2])

                if self.version == 2:
                    self.ssp.cur.data.temp[count] = float(data[3])
                    self.ssp.cur.data.sal[count] = float(data[4])
                    # The fifth field is an extra (unused?) field
                    self.ssp.cur.more.sa['Depth'][count] = float(data[1])
                    self.ssp.cur.more.sa['Flag'][count] = float(data[6])

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + count))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + count))
                continue

            count += 1

        self.ssp.cur.data_resize(count)
