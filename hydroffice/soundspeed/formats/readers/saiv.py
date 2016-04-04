from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt
import logging

logger = logging.getLogger(__name__)


from .abstract import AbstractTextReader
from ...profile.dicts import Dicts


class Saiv(AbstractTextReader):
    """Saiv reader -> CTD style

    Info: http://www.saivas.no/index.asp
    """

    def __init__(self):
        super(Saiv, self).__init__()
        self._ext.add('txt')

        self.tk_header = 'Ser\tMeas'
        self.tk_depth = 'Press'
        self.tk_speed = 'S. vel.'
        self.tk_temp = 'Temp'
        self.tk_sal = 'Sal.'
        self.tk_date = 'Date'
        self.tk_time = 'Time'
        self.tk_probe_type = 'From file:'

    def read(self, data_path, up_or_down=Dicts.ssp_directions['down']):
        logger.debug('*** %s ***: start' % self.driver)

        self.up_or_down = up_or_down

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize probe/sensor type
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['CTD']
        self.ssp.cur.meta.probe_type = Dicts.probe_types['S2']

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """Parsing header: field header"""
        logger.debug('parsing header')

        # control flags
        has_date = False
        has_time = False
        has_depth = False
        has_speed = False
        has_temp = False
        has_sal = False

        for line in self.lines:

            if not line:  # skip empty lines
                continue

            if line[:len(self.tk_header)] == self.tk_header:  # field headers
                col = 0  # field column
                for field_type in line.split('\t'):  # split fields by tab
                    field_type = field_type.strip()
                    if len(field_type) == 0:
                        continue
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
                    elif field_type == self.tk_date:
                        has_date = True
                    elif field_type == self.tk_time:
                        has_time = True
                    else:
                        self.more_fields.append(field_type)
                    col += 1
                self.samples_offset += 1
                logger.debug("samples offset: %s" % self.samples_offset)
                break

            self.samples_offset += 1

        # sample fields checks
        if (not has_date) or (not has_time):
            logger.warning("Missing data/time field: %s/%s" % (self.tk_date, self.tk_time))
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

        # initialize data sample structures
        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)
        # initialize additional fields
        self.ssp.cur.init_more(self.more_fields)

    def _parse_body(self):
        """Parsing samples: depth, speed, temp, sal"""
        logger.debug('parsing body')

        count = 0
        has_valid_time = False
        for line in self.lines[self.samples_offset:len(self.lines)]:

            # skip empty lines
            if len(line.split()) == 0:
                continue

            data = line.split('\t')

            # get date/time
            if not has_valid_time:
                try:
                    date_string = data[self.field_index[self.tk_date]]  # date
                    month = int(date_string.split('/')[1])
                    day = int(date_string.split('/')[0])
                    year = int(date_string.split('/')[2])
                    time_string = data[self.field_index[self.tk_time]]
                    hour = int(time_string.split(':')[0])
                    minute = int(time_string.split(':')[1])
                    second = int(time_string.split(':')[2])
                    self.ssp.cur.meta.utc_time = dt.datetime(year=year, month=month, day=day,
                                                             hour=hour, minute=minute, second=second)
                    has_valid_time = True
                except Exception as e:
                    logger.warning('unable to retrieve date/time at line #%s' % (self.samples_offset + count))

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
