from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime as dt
import logging

logger = logging.getLogger(__name__)


from .abstract import AbstractTextReader
from ...profile.dicts import Dicts
from ...base.callbacks import CliCallbacks


class Seabird(AbstractTextReader):
    """Seabird reader -> CTD style

    Info: http://www.seabird.com/
    """

    def __init__(self):
        super(Seabird, self).__init__()
        self.desc = "Seabird"
        self._ext.add('cnv')

        self.tk_start_data = '*END*'
        self.tk_time = '* System UpLoad Time'
        self.tk_time_2 = '* NMEA UTC (Time)'
        self.tk_filename = '* FileName'
        self.tk_latitude = '* NMEA Latitude ='
        self.tk_longitude = '* NMEA Longitude ='
        self.tk_field_name = '# name'

        self.tk_depth = 'depSM'
        self.tk_speed = 'svCM'
        self.tk_temp = ''  # will be assigned during the header parsing
        self.tk_sal = 'sal00'

    def read(self, data_path, settings, callbacks=CliCallbacks()):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize probe/sensor type
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['CTD']
        self.ssp.cur.meta.probe_type = Dicts.probe_types['SBE']

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """Parsing header: field header, time, latitude, longitude

        The Castaway header has field starting with '%'
        """
        logger.debug('parsing header')

        # control flags
        has_depth = False
        has_speed = False
        has_temp = False
        has_sal = False
        system_time = None

        for line in self.lines:

            if not line:  # skip empty lines
                continue

            if line[:len(self.tk_start_data)] == self.tk_start_data:
                self.samples_offset += 1
                logger.debug("samples offset: %s" % self.samples_offset)
                break

            elif line[:len(self.tk_field_name)] == self.tk_field_name:
                column = line.split()[2]
                field_type = line.split()[4].split(":")[0]
                self.field_index[field_type] = int(column)
                if field_type == self.tk_depth:
                    has_depth = True
                elif field_type == self.tk_speed:
                    has_speed = True
                elif field_type == "t090C" or field_type == "tv290C":
                    has_temp = True
                    self.tk_temp = field_type
                elif field_type == self.tk_sal:
                    has_sal = True

            elif line[:len(self.tk_time)] == self.tk_time:  # system time
                if self.ssp.cur.meta.utc_time:  # we prefer utc time
                    continue
                try:
                    year = int(line.split()[-2])
                    day = int(line.split()[-3])
                    month_name = line.split()[-4]
                    month = dt.strptime(month_name, '%b').month
                    time_string = line.split()[-1]
                    hour, minute, second = [int(i) for i in time_string.split(':')]
                    system_time = dt(year, month, day, hour, minute, second)
                except ValueError:
                    logger.info("unable to parse system date and time from line #%s" % self.samples_offset)

            elif line[:len(self.tk_time_2)] == self.tk_time_2:  # utc time
                try:
                    year = int(line.split()[-2])
                    day = int(line.split()[-3])
                    month_name = line.split()[-4]
                    month = dt.strptime(month_name, '%b').month
                    time_string = line.split()[-1]
                    hour, minute, second = [int(i) for i in time_string.split(':')]
                    self.ssp.cur.meta.utc_time = dt(year, month, day, hour, minute, second)
                except ValueError:
                    logger.info("unable to parse UTC date and time from line #%s" % self.samples_offset)

            elif line[:len(self.tk_latitude)] == self.tk_latitude:  # latitude
                try:
                    deg = float(line.split()[-3])
                    min_deg = float(line.split()[-2])
                    hemisphere = line.split()[-1]
                    latitude = deg + min_deg/60.0
                    if hemisphere == "S":
                        latitude *= -1
                except ValueError:
                    logger.error("unable to parse latitude from line #%s" % self.samples_offset)

            elif line[:len(self.tk_longitude)] == self.tk_longitude:  # longitude
                try:
                    deg = float(line.split()[-3])
                    min_deg = float(line.split()[-2])
                    hemisphere = line.split()[-1]
                    longitude = deg + min_deg/60.0
                    if hemisphere == "W":
                        longitude *= -1
                except ValueError:
                    logger.error("unable to parse longitude from line #%s" % self.samples_offset)

            self.samples_offset += 1

        # sample fields checks
        if not has_depth:
            raise RuntimeError("Missing depth field: %s" % self.tk_depth)
        if not has_speed:
            raise RuntimeError("Missing sound speed field: %s" % self.tk_speed)
        if not has_temp:
            raise RuntimeError("Missing temperature field: %s" % self.tk_temp)
        if not has_sal:
            raise RuntimeError("Missing salinity field: %s" % self.tk_sal)
        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path
        if (not self.ssp.cur.meta.utc_time) and system_time:
            self.ssp.cur.meta.utc_time = system_time

        # initialize data sample fields
        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)
        # initialize additional fields
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
                self.ssp.cur.data.depth[count] = float(data[self.field_index[self.tk_depth]])
                self.ssp.cur.data.speed[count] = float(data[self.field_index[self.tk_speed]])
                self.ssp.cur.data.temp[count] = float(data[self.field_index[self.tk_temp]])
                self.ssp.cur.data.sal[count] = float(data[self.field_index[self.tk_sal]])

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + count))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + count))
                continue

            # additional data field
            try:
                for mf in self.more_fields:
                    self.ssp.cur.more.sa[mf][count] = float(data[self.field_index[mf]])
            except Exception as e:
                logger.debug("issue in reading additional data fields: %s -> skipping" % e)

            count += 1

        self.ssp.cur.data_resize(count)
