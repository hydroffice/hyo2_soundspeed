import datetime as dt
import locale
import logging

logger = logging.getLogger(__name__)

from hyo2.soundspeed.formats.readers.abstract import AbstractTextReader
from hyo2.soundspeed.profile.dicts import Dicts
from hyo2.soundspeed.base.callbacks.cli_callbacks import CliCallbacks


class SeaAndSun(AbstractTextReader):
    """Sea&Sun Technology reader -> CTD style

    Info: https://sea-sun-tech.com/technology.html
    """

    # A dictionary to resolve probe type from probe type token
    probe_dict = {
        'CTD': Dicts.probe_types['SST-CTD'],
        'CTP': Dicts.probe_types['SST-CTP'],
        'CTM': Dicts.probe_types['SST-MEM']
    }
    
    def __init__(self):
        super(SeaAndSun, self).__init__()
        self.desc = "SeaAndSun"
        self._ext.add('tob')

        # header tokens
        self.tk_datasets = '; Datasets'
        self.tk_header = 'Sea & Sun Technology'
        self.tk_serial = '001'

        # sample field tokens
        self.tk_pressure = 'Press'
        self.tk_sal = 'SALIN'
        self.tk_temp = 'Temp'
        self.tk_speed = 'SOUND'

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize sensor type
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['CTD']

        self._read(data_path=data_path, encoding='latin')  # Idronaut seems to have a specific encoding
        self._parse_header()
        self._parse_body()

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """Parsing header: field header, filename, time, latitude, longitude, probe type, serial number"""
        logger.debug('parsing header')

        # control flags
        has_pressure = False
        has_speed = False
        has_temp = False
        has_sal = False

        time_string = None
        date_string = None

        for line_idx, line in enumerate(self.lines):

            # check if the input file has a known header
            if line_idx == 0:
                if self.tk_header not in line:
                    raise RuntimeError("Unknown header for input file: %s" % line)

            # these are weak solutions to retrieve the header content

            elif line_idx == 2:  # [date and] time
                time_string = line.split()[-1].strip()
                try:
                    old_loc = locale.getlocale(locale.LC_TIME)
                    locale.setlocale(locale.LC_TIME, locale="German")
                    date_tuple = dt.datetime.strptime(line.split(",")[-1].strip(), "%d. %B %Y %H:%M:%S")
                    date_string = date_tuple.strftime("%d.%m.%Y")
                    locale.setlocale(locale.LC_TIME, old_loc)
                except Exception as e:
                    logger.info("Fail to interpret date from German: %s" % e)
                    date_string = None

            elif line_idx == 9:  # latitude and longitude
                try:
                    lat_str = line[21:34]
                    lat_tokens = lat_str.split()
                    # logger.debug("lat: %s" % (lat_tokens,))
                    lat_deg = int(lat_tokens[0].split('\xb0')[0])
                    lat_min = float(lat_tokens[1].split('\'')[0])
                    if lat_tokens[2] == "S":
                        lat_sign = -1.0
                    else:
                        lat_sign = 1.0

                    self.ssp.cur.meta.latitude = lat_sign * (lat_deg + lat_min / 60.0)

                except Exception as e:
                    logger.warning("unable to retrieve latitude from %s, %s" % (line, e))

                try:
                    lon_str = line[47:60]
                    lon_tokens = lon_str.split()
                    # logger.debug("lon: %s" % (lon_tokens,))
                    lon_deg = int(lon_tokens[0].split('\xb0')[0])
                    lon_min = float(lon_tokens[1].split('\'')[0])
                    if lon_tokens[2] == "W":
                        lon_sign = -1.0
                    else:
                        lon_sign = 1.0

                    self.ssp.cur.meta.longitude = lon_sign * (lon_deg + lon_min / 60.0)

                except Exception as e:
                    logger.warning("unable to retrieve longitude from %s, %s" % (line, e))

            elif line_idx == 17:   # probe type and serial number
               if line[:len(self.tk_serial)] == self.tk_serial:
                   try:
                       probe_sn_tokens = line.split()[1]
                       self.ssp.cur.meta.probe_type = self.probe_dict[probe_sn_tokens[:3]]
                       self.ssp.cur.meta.sn = probe_sn_tokens[3:]
                   except KeyError:
                       logger.warning("unable to recognize probe type from line #%s" % line_idx)
                    
            if not line:  # skip empty lines
                continue

            if line[:len(self.tk_datasets)] == self.tk_datasets:

                datasets_fields = line.split()
                # logger.debug(datasets_fields)

                for field_idx, field_type in enumerate(datasets_fields):

                    self.field_index[field_type] = field_idx - 1  # -1 since the first field is ';'
                    if field_type == self.tk_pressure:
                        has_pressure = True
                    elif field_type == self.tk_temp:
                        has_temp = True
                    elif field_type == self.tk_sal:
                        has_sal = True
                    elif field_type == self.tk_speed:
                        has_speed = True

                if has_pressure and has_speed:
                    self.samples_offset = line_idx + 3
                    logger.debug("samples offset: %s" % self.samples_offset)
                    break

        if (time_string is not None) and (date_string is not None):
            try:
                self.ssp.cur.meta.utc_time = dt.datetime.strptime(date_string + ' ' + time_string, "%d.%m.%Y %H:%M:%S")

            except Exception:
                logger.warning("issue in retrieving the timestamp")

        # sample fields checks
        if not has_pressure:
            raise RuntimeError("Missing pressure field: %s" % self.tk_pressure)
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

    def _parse_body(self):
        """Parsing samples: depth, speed, temp, sal"""
        logger.debug('parsing body')

        count = 0
        for line in self.lines[self.samples_offset:len(self.lines)]:

            # skip empty lines
            if len(line.split()) == 0:
                continue

            data = line.split()
            # required data fields
            try:
                self.ssp.cur.data.pressure[count] = float(data[self.field_index[self.tk_pressure]])
                self.ssp.cur.data.speed[count] = float(data[self.field_index[self.tk_speed]])
                self.ssp.cur.data.temp[count] = float(data[self.field_index[self.tk_temp]])
                self.ssp.cur.data.sal[count] = float(data[self.field_index[self.tk_sal]])

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + count))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + count))
                continue

            count += 1

        self.ssp.cur.data_resize(count)
