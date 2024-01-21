import datetime as dt
import logging

logger = logging.getLogger(__name__)

from hyo2.soundspeed.formats.readers.abstract import AbstractTextReader
from hyo2.soundspeed.profile.dicts import Dicts
from hyo2.soundspeed.base.callbacks.cli_callbacks import CliCallbacks


class RBR(AbstractTextReader):
    """RBR reader -> CTD style

    Info: https://rbr-global.com/products/standard-loggers/rbrmaestro
    """

    def __init__(self):
        super().__init__()
        self.desc = "RBR"
        self.ext.add('txt')

        # header tokens
        self.tk_cast_time = 'time'

        # body tokens
        self.tk_depth = 'depth'
        self.tk_sal = 'salinity'
        self.tk_temp = 'temperature'
        self.tk_speed = 'speed of sound'
        self.tk_pressure = 'pressure'
        self.tk_conductivity = 'conductivity'

        # control flags
        self.has_depth = False
        self.has_speed = False
        self.has_temp = False
        self.has_sal = False
        self.has_pressure = False
        self.has_conductivity = False

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize probe/sensor type
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['CTD']
        self.ssp.cur.meta.probe_type = Dicts.probe_types['RBR']

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

        if self.lines[0][:len(self.tk_cast_time)].lower() != self.tk_cast_time:
            raise RuntimeError('Unknown/unsupported RBR format starting with %s'
                               % self.lines[0][:len(self.tk_cast_time)])

        fields = self.lines[0].split(",")
        if len(fields) < 3:
            raise RuntimeError('Unknown/unsupported header in RBR format: %s' % self.lines[0])

        col = 0  # field column
        for field in fields:  # split fields by comma
            field = field.lower()
            self.field_index[field] = col
            if field == self.tk_depth:
                self.has_depth = True
                self.more_fields.insert(0, field)  # prepend depth to additional fields
            elif field == self.tk_speed:
                self.has_speed = True
            elif field == self.tk_temp:
                self.has_temp = True
            elif field == self.tk_sal:
                self.has_sal = True
            elif field == self.tk_pressure:
                self.has_pressure = True
            elif field == self.tk_conductivity:
                self.has_conductivity = True
            elif field == self.tk_cast_time:
                pass
            else:
                self.more_fields.append(field)
            col += 1

        self.samples_offset += 1
        logger.debug("samples offset: %s" % self.samples_offset)

        # retrieve the first timestamp from the data
        for idx, line in enumerate(self.lines[self.samples_offset:self.samples_offset+3]):

            # skip empty lines
            if len(line.split()) == 0:
                continue

            try:
                field = line.split(",")[0]
                if len(field) != 0:
                    ymd = field.split()[0].strip()
                    year = int(ymd.split("-")[0])
                    month = int(ymd.split("-")[1])
                    day = int(ymd.split("-")[2])
                    time_string = field.split()[1].strip()
                    hour = int(time_string.split(":")[0])
                    minute = int(time_string.split(":")[1])
                    second = int(float(time_string.split(":")[2]))
                    self.ssp.cur.meta.utc_time = dt.datetime(year, month, day, hour, minute, second)
                    logger.debug('cast timestamp: %s' % self.ssp.cur.meta.utc_time)
            except ValueError:
                logger.info("unable to parse date and time from line #%s" % (idx + self.samples_offset))

        # sample fields checks
        if not self.has_depth and not self.has_pressure:
            raise RuntimeError("Missing depth/pressure field: %s/%s" % (self.tk_depth, self.tk_pressure))
        if not self.has_speed:
            if not self.has_temp:
                raise RuntimeError("Missing required fields: %s or %s" % (self.tk_speed, self.tk_temp))
            else:
                if self.has_sal:
                    self.ssp.cur.meta.sensor_type = Dicts.sensor_types['XCTD']
                else:
                    self.ssp.cur.meta.sensor_type = Dicts.sensor_types['XBT']
        else:
            if not self.has_temp:
                self.ssp.cur.meta.sensor_type = Dicts.sensor_types['SVP']
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
                if self.has_depth:
                    self.ssp.cur.data.depth[count] = float(data[self.field_index[self.tk_depth]])
                if self.has_speed:
                    self.ssp.cur.data.speed[count] = float(data[self.field_index[self.tk_speed]])
                if self.has_temp:
                    self.ssp.cur.data.temp[count] = float(data[self.field_index[self.tk_temp]])
                if self.has_sal:
                    self.ssp.cur.data.sal[count] = float(data[self.field_index[self.tk_sal]])
            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + count))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + count))
                continue

            # pressure and conductivity
            try:
                if self.has_pressure:
                    self.ssp.cur.data.pressure[count] = float(data[self.field_index[self.tk_pressure]])
                if self.has_conductivity:
                    self.ssp.cur.data.conductivity[count] = float(data[self.field_index[self.tk_conductivity]])
            except Exception as e:
                logger.debug("issue in reading pressure and conductivity: %s -> skipping" % e)

            # additional data field
            try:
                for mf in self.more_fields:
                    self.ssp.cur.more.sa[mf][count] = float(data[self.field_index[mf]])
            except Exception as e:
                logger.debug("issue in reading additional data fields: %s -> skipping" % e)

            count += 1

        self.ssp.cur.data_resize(count)
