from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt
import logging

logger = logging.getLogger(__name__)


from ..abstract import AbstractTextReader
from ...profile.dicts import Dicts


class Valeport(AbstractTextReader):
    """Valeport reader"""

    # A dictionary to resolve sensor type from probe type
    sensor_dict = {
        Dicts.probe_types['MONITOR SVP 500']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MIDAS SVP 6000']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MiniSVP']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['Unknown']: Dicts.sensor_types["Unknown"]
    }

    def __init__(self):
        super(Valeport, self).__init__()
        self._ext.add('000')
        self._ext.add('txt')

        self.tk_start_data = ""
        self.tk_time = ""
        self.tk_latitude = 'Latitude'
        self.tk_probe_type = ""

    def read(self, data_path):
        logger.debug('*** %s ***: start' % self.driver)

        self.init_data()  # create a new empty profile

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        logger.debug('parsing header')

        if self.lines[0][:3] == 'Now':  # MiniSVP
            self._mini_header()
        else:  # MIDAS or Monitor
            self._midas_header()

    def _mini_header(self):
        self.tk_start_data = 'Pressure units:'
        self.tk_time = 'Now'
        self.tk_probe_type = 'MiniSVP:'

        for line in self.lines:
            if line[:len(self.tk_start_data)] == self.tk_start_data:
                self.samples_offset += 1
                break

            elif line[:len(self.tk_time)] == self.tk_time:
                try:
                    date_string = line.split()[1]
                    time_string = line.split()[2]
                    month = int(date_string.split('/')[1])
                    day = int(date_string.split('/')[0])
                    year = int(date_string.split('/')[2])
                    hour = int(time_string.split(':')[0])
                    minute = int(time_string.split(':')[1])
                    second = int(time_string.split(':')[2])
                    if (year is not None) and (hour is not None):
                        self.ssp.meta.utc_time = dt.datetime(year, month, day, hour, minute, second)
                except ValueError:
                    logger.warning("unable to parse date and time from line #%s" % self.samples_offset)

            elif line[:len(self.tk_latitude)] == self.tk_latitude:
                try:
                    self.ssp.meta.latitude = float(line.split(':')[-1])
                except ValueError:
                    logger.warning("unable to parse latitude from line #%s" % self.samples_offset)

            elif line[:len(self.tk_probe_type)] == self.tk_probe_type:
                self.ssp.meta.probe_type = Dicts.probe_types['MiniSVP']
                try:
                    self.ssp.meta.sensor_type = self.sensor_dict[self.ssp.meta.probe_type]
                except KeyError:
                    logger.warning("unable to recognize probe type from line #%s" % self.samples_offset)
                    self.ssp.meta.sensor_type = Dicts.sensor_types['Unknown']
            self.samples_offset += 1

        if not self.ssp.meta.original_path:
            self.ssp.meta.original_path = self.fid.path

        # initialize data sample structures
        self.ssp.init_data(len(self.lines) - self.samples_offset)
        # initialize additional fields
        self.ssp.init_more(self.more_fields)

    def _midas_header(self):
        self.tk_start_data = 'Date / Time'
        self.tk_time = 'Time Stamp :'
        self.tk_probe_type = 'Model Name :'

        for line in self.lines:

            if line[:len(self.tk_start_data)] == self.tk_start_data:
                self.samples_offset += 1
                break

            elif line[:len(self.tk_time)] == self.tk_time:
                try:
                    date_string = line.split()[-2]
                    time_string = line.split()[-1]
                    day, month, year = [int(i) for i in date_string.split('/')]
                    hour, minute, second = [int(i) for i in time_string.split(':')]
                    self.ssp.meta.utc_time = dt.datetime(year, month, day, hour, minute, second)
                except ValueError:
                    logger.warning("unable to parse time from line #%s" % self.samples_offset)

            elif line[:len(self.tk_probe_type)] == self.tk_probe_type:
                try:
                    self.ssp.meta.probe_type = Dicts.probe_types[line.split(':')[-1].strip()]
                except (ValueError, KeyError):
                    logger.warning("unable to parse probe type from line #%s" % self.samples_offset)
                    self.ssp.meta.probe_type = Dicts.probe_types['Unknown']
                try:
                    self.ssp.meta.sensor_type = self.sensor_dict[self.ssp.meta.probe_type]
                except KeyError:
                    logger.warning("unable to find sensor type from line #%s" % self.samples_offset)
                    self.ssp.meta.sensor_type = Dicts.sensor_types['Unknown']

            self.samples_offset += 1

        if not self.ssp.meta.original_path:
            self.ssp.meta.original_path = self.fid.path

        # initialize data sample structures
        self.ssp.init_data(len(self.lines) - self.samples_offset)
        # initialize additional fields
        self.ssp.init_more(self.more_fields)

    def _parse_body(self):
        logger.debug('parsing body')

        if self.lines[0][:3] == 'Now':  # MiniSVP
            self._mini_body()
        else:  # MIDAS or Monitor
            self._midas_body()

    def _mini_body(self):
        count = 0
        for line in self.lines[self.samples_offset:len(self.lines)]:
            try:
                data = line.split()
                # Skipping invalid data (above water, negative temperature or crazy sound speed)
                if float(data[0]) < 0.0 or float(data[1]) < -2.0 or float(data[2]) < 1400.0 or float(data[2]) > 1650.0:
                    continue

                self.ssp.data.depth[count] = float(data[0])
                self.ssp.data.temp[count] = float(data[1])
                self.ssp.data.speed[count] = float(data[2])
                count += 1

            except ValueError:
                logger.error("unable to parse from line #%s" % self.samples_offset)
                continue

        self.ssp.resize(count)

    def _midas_body(self):

        count = 0
        for line in self.lines[self.samples_offset:len(self.lines)]:
            try:
                # In case an incomplete file comes through
                if self.ssp.meta.sensor_type == Dicts.sensor_types["SVPT"]:
                    data = line.split()

                    if data[2] == 0.0:  # sound speed
                        continue

                    # s_date = data[0]
                    # s_time = data[1]
                    self.ssp.data.speed[count] = data[2]
                    self.ssp.data.depth[count] = data[3]
                    self.ssp.data.temp[count] = data[4]

            except ValueError:
                logger.error("unable to parse from line #%s" % self.samples_offset)
                continue

            count += 1

        self.ssp.resize(count)

