from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt
import logging

logger = logging.getLogger(__name__)


from .abstract import AbstractTextReader
from ...profile.dicts import Dicts
from ...base.callbacks import Callbacks


class Valeport(AbstractTextReader):
    """Valeport reader"""

    # A dictionary to resolve sensor type from probe type
    sensor_dict = {
        Dicts.probe_types['MONITOR SVP 500']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MIDAS SVP 6000']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MIDAS SVX2 1000']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MIDAS SVX2 3000']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MiniSVP']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['Unknown']: Dicts.sensor_types["Unknown"]
    }

    def __init__(self):
        super(Valeport, self).__init__()
        self.desc = "Valeport Monitor/Midas/MiniSVP"
        self._ext.add('000')
        self._ext.add('txt')

        self.tk_start_data = ""
        self.tk_time = ""
        self.tk_latitude = 'Latitude'
        self.tk_probe_type = ""

    def read(self, data_path, settings, callbacks=Callbacks()):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.fix()
        if self.ssp.cur.meta.probe_type not in [Dicts.probe_types['MiniSVP']]:
            self.ssp.cur.calc_data_depth()
        if self.ssp.cur.meta.probe_type not \
                in [Dicts.probe_types['MIDAS SVX2 1000'], Dicts.probe_types['MIDAS SVX2 3000']]:
            self.ssp.cur.calc_salinity()
        self.finalize()

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
                        self.ssp.cur.meta.utc_time = dt.datetime(year, month, day, hour, minute, second)
                except ValueError:
                    logger.warning("unable to parse date and time from line #%s" % self.samples_offset)

            elif line[:len(self.tk_latitude)] == self.tk_latitude:
                try:
                    self.ssp.cur.meta.latitude = float(line.split(':')[-1])
                except ValueError:
                    logger.warning("unable to parse latitude from line #%s" % self.samples_offset)

            elif line[:len(self.tk_probe_type)] == self.tk_probe_type:
                self.ssp.cur.meta.probe_type = Dicts.probe_types['MiniSVP']
                try:
                    self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]
                except KeyError:
                    logger.warning("unable to recognize probe type from line #%s" % self.samples_offset)
                    self.ssp.cur.meta.sensor_type = Dicts.sensor_types['Unknown']
            self.samples_offset += 1

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample structures
        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)
        # initialize additional fields
        self.ssp.cur.init_more(self.more_fields)

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
                    self.ssp.cur.meta.utc_time = dt.datetime(year, month, day, hour, minute, second)
                except ValueError:
                    logger.warning("unable to parse time from line #%s" % self.samples_offset)

            elif line[:len(self.tk_probe_type)] == self.tk_probe_type:
                try:
                    self.ssp.cur.meta.probe_type = Dicts.probe_types[line.split(':')[-1].strip()]
                except (ValueError, KeyError):
                    logger.warning("unable to parse probe type from line #%s" % self.samples_offset)
                    self.ssp.cur.meta.probe_type = Dicts.probe_types['Unknown']
                try:
                    self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]
                except KeyError:
                    logger.warning("unable to find sensor type from line #%s" % self.samples_offset)
                    self.ssp.cur.meta.sensor_type = Dicts.sensor_types['Unknown']

            self.samples_offset += 1

        if (self.ssp.cur.meta.probe_type == Dicts.probe_types['MIDAS SVX2 1000']) or \
                (self.ssp.cur.meta.probe_type == Dicts.probe_types['MIDAS SVX2 3000']):
            self.more_fields.append('Pressure')
            self.more_fields.append('Conductivity')
        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample structures
        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)
        # initialize additional fields
        self.ssp.cur.init_more(self.more_fields)

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

                self.ssp.cur.data.depth[count] = float(data[0])
                self.ssp.cur.data.temp[count] = float(data[1])
                self.ssp.cur.data.speed[count] = float(data[2])
                count += 1

            except ValueError:
                logger.error("unable to parse from line #%s" % self.samples_offset)
                continue

        self.ssp.cur.data_resize(count)

    def _midas_body(self):

        count = 0
        for line in self.lines[self.samples_offset:len(self.lines)]:
            try:
                # In case an incomplete file comes through
                if self.ssp.cur.meta.sensor_type == Dicts.sensor_types["SVPT"]:
                    data = line.split()

                    if float(data[2]) == 0.0:  # sound speed
                        continue

                    # s_date = data[0]
                    # s_time = data[1]
                    self.ssp.cur.data.speed[count] = data[2]
                    self.ssp.cur.data.depth[count] = data[3]
                    self.ssp.cur.data.temp[count] = data[4]

                    if (self.ssp.cur.meta.probe_type == Dicts.probe_types['MIDAS SVX2 1000']) or \
                            (self.ssp.cur.meta.probe_type == Dicts.probe_types['MIDAS SVX2 3000']):
                        self.ssp.cur.data.sal[count] = data[6]

                        # additional data field
                        try:
                            self.ssp.cur.more.sa['Pressure'][count] = float(data[3])  # pressure
                            self.ssp.cur.more.sa['Conductivity'][count] = float(data[5])  # conductivity
                        except Exception as e:
                            logger.debug("issue in reading additional data fields: %s -> skipping" % e)

            except ValueError:
                logger.error("unable to parse from line #%s" % self.samples_offset)
                continue

            count += 1

        self.ssp.cur.data_resize(count)

