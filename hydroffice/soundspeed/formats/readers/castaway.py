from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt
import logging

logger = logging.getLogger(__name__)


from .abstract import AbstractTextReader
from ...profile.dicts import Dicts
from ...base.callbacks import CliCallbacks


class Castaway(AbstractTextReader):
    """Castaway reader -> CTD style

    Info: http://www.sontek.com/productsdetail.php?CastAway-CTD-11
    """

    def __init__(self):
        super(Castaway, self).__init__()
        self.desc = "Castaway"
        self.ext.add('csv')

        # header tokens
        self.tk_filename = '% File name'
        self.tk_cast_time = '% Cast time (UTC)'
        self.tk_latitude = '% Start latitude'
        self.tk_longitude = '% Start longitude'

        # body tokens
        self.tk_depth = 'Depth'
        self.tk_sal = 'Salinity'
        self.tk_temp = 'Temperature'
        self.tk_speed = 'Sound'

    def read(self, data_path, settings, callbacks=CliCallbacks()):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize probe/sensor type
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['CTD']
        self.ssp.cur.meta.probe_type = Dicts.probe_types['Castaway']

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """Parsing header: field header, time, latitude, longitude"""
        logger.debug('parsing header')

        # control flags
        has_depth = False
        has_speed = False
        has_temp = False
        has_sal = False

        for line in self.lines:

            if not line:  # skip empty lines
                self.samples_offset += 1
                continue

            if line[0] != '%':  # field headers
                col = 0  # field column
                for field in line.split(","):  # split fields by comma
                    field_type = field.split()[0]  # take only the first word
                    self.field_index[field_type] = col
                    if field_type == self.tk_depth:
                        has_depth = True
                        self.more_fields.insert(0, field_type)  # prepend depth to additional fields
                    elif field_type == self.tk_speed:
                        has_speed = True
                    elif field_type == self.tk_temp:
                        has_temp = True
                    elif field_type == self.tk_sal:
                        has_sal = True
                    else:
                        self.more_fields.append(field_type)
                    col += 1
                self.samples_offset += 1
                logger.debug("samples offset: %s" % self.samples_offset)
                break

            elif line[:len(self.tk_cast_time)] == self.tk_cast_time:  # utc time
                try:
                    field = line.split(",")[-1]
                    if len(field) != 0:
                        ymd = field.split()[-2]
                        year = int(ymd.split("-")[-3])
                        month = int(ymd.split("-")[-2])
                        day = int(ymd.split("-")[-1])
                        time_string = field.split()[-1].strip()
                        hour, minute, second = [int(i) for i in time_string.split(':')]
                        self.ssp.cur.meta.utc_time = dt.datetime(year, month, day, hour, minute, second)
                except ValueError:
                    logger.info("unable to parse date and time from line #%s" % self.samples_offset)

            elif line[:len(self.tk_latitude)] == self.tk_latitude:
                try:
                    lat_str = line.split(",")[-1]
                    if len(lat_str) != 0:
                        self.ssp.cur.meta.latitude = float(lat_str)
                except ValueError:
                    logger.error("unable to parse latitude from line #%s" % self.samples_offset)

            elif line[:len(self.tk_longitude)] == self.tk_longitude:
                try:
                    lon_str = line.split(",")[-1]
                    if len(lon_str) != 0:
                        self.ssp.cur.meta.longitude = float(lon_str)
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

            data = line.split(",")
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
