import datetime as dt
import logging

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.formats.readers.abstract import AbstractTextReader
from hydroffice.soundspeed.profile.dicts import Dicts
from hydroffice.soundspeed.base.callbacks.cli_callbacks import CliCallbacks


class Idronaut(AbstractTextReader):
    """Idronaut reader -> CTD style

    Info: http://www.idronaut.it/cms/view/products/multiparameter_probes/oceanographic_ctd_probes
        /ocean_seven_316_i_plus_i_/s310
    """

    def __init__(self):
        super(Idronaut, self).__init__()
        self.desc = "Idronaut"
        self._ext.add('txt')

        # header tokens
        self.tk_cast = 'cast'
        self.tk_probe_type = 'cast probe type'
        self.tk_start_time = 'cast start time'
        self.tk_start_latitude = 'cast start latitude'
        self.tk_start_longitude = 'cast start longitude'

        # sample field tokens
        self.tk_depth = 'Depth'
        self.tk_sal = 'Salinity'
        self.tk_temp = 'Temperature'
        self.tk_speed = 'Sound Velocity (calc)'

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize probe/sensor type
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['CTD']
        self.ssp.cur.meta.probe_type = Dicts.probe_types['Idronaut']

        self._read(data_path=data_path, encoding='latin')  # Idronaut seems to have a specific encoding
        self._parse_header()
        self._parse_body()

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """Parsing header: field header, filename, time, latitude, longitude"""
        logger.debug('parsing header')

        # control flags
        has_depth = False
        has_speed = False
        has_temp = False
        has_sal = False

        for line in self.lines:

            if not line:  # skip empty lines
                continue

            tabbed_fields = [tf.strip() for tf in line.split('\t')]  # we assume that the field header has >3 fields
            if len(tabbed_fields) > 3:

                col = 0
                for field_type in tabbed_fields:
                    self.field_index[field_type] = col
                    if field_type == self.tk_depth:
                        has_depth = True
                        self.more_fields.insert(0, field_type)  # prepend depth for additional fields
                    elif field_type == self.tk_temp:
                        has_temp = True
                    elif field_type == self.tk_sal:
                        has_sal = True
                    elif field_type == self.tk_speed:
                        has_speed = True
                    else:
                        self.more_fields.append(field_type)
                    col += 1

                if has_depth and has_speed:
                    self.samples_offset += 1
                    logger.debug("samples offset: %s" % self.samples_offset)
                    break

            elif line[:len(self.tk_start_time)] == self.tk_start_time:
                try:
                    date_string = line.split()[3]
                    month = int(date_string.split('/')[1])
                    day = int(date_string.split('/')[0])
                    year = int(date_string.split('/')[2])
                except ValueError:
                    logger.warning("invalid cast date string at row #%s" % self.samples_offset)
                    continue

                try:
                    time_string = line.split()[4]
                    hour = int(time_string.split(':')[0])
                    minute = int(time_string.split(':')[1])
                    second = int(time_string.split(':')[2])
                except ValueError:
                    logger.warning("invalid cast time string at row #%s" % self.samples_offset)
                    continue

                self.ssp.cur.meta.utc_time = dt.datetime(year, month, day, hour, minute, second)

            elif line[:len(self.tk_start_latitude)] == self.tk_start_latitude:
                lat_token = line.split()[-1]
                if len(lat_token) == 0:
                    self.samples_offset += 1
                    continue
                lat_deg = int(lat_token.split('\xb0')[0])
                lat_min = int(lat_token.split('\'')[0].split('\xb0')[1])
                lat_sec = float(lat_token.split('\'')[1])

                if lat_deg < 0:
                    lat_sign = -1.0
                    lat_deg = abs(lat_deg)
                else:
                    lat_sign = 1.0

                self.ssp.cur.meta.latitude = lat_sign * (lat_deg + lat_min / 60.0 + lat_sec / 3600.0)

            elif line[:len(self.tk_start_longitude)] == self.tk_start_longitude:
                lon_token = line.split()[-1]
                if len(lon_token) == 0:
                    self.samples_offset += 1
                    continue
                lon_deg = int(lon_token.split('\xb0')[0])
                lon_min = int(lon_token.split('\'')[0].split('\xb0')[1])
                lon_sec = float(lon_token.split('\'')[1])

                if lon_deg < 0:
                    lon_sign = -1.0
                    lon_deg = abs(lon_deg)
                else:
                    lon_sign = 1.0
                self.ssp.cur.meta.longitude = lon_sign * (lon_deg + lon_min / 60.0 + lon_sec / 3600.0)

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

            data = line.split('\t')
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
