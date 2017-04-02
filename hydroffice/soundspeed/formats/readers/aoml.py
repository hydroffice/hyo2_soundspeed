import re
import datetime as dt
import logging

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.formats.readers.abstract import AbstractTextReader
from hydroffice.soundspeed.profile.dicts import Dicts
from hydroffice.soundspeed.base.callbacks.cli_callbacks import CliCallbacks


class Aoml(AbstractTextReader):
    """AOML AMVER-SEAS reader"""

    # A dictionary to resolve sensor type from probe type
    sensor_dict = {
        Dicts.probe_types["Deep Blue"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-10"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-11 (Fine Structure)"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-4"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-5"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-5/20"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-7"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["XSV-01"]: Dicts.sensor_types["XSV"],
        Dicts.probe_types["XSV-02"]: Dicts.sensor_types["XSV"],
        Dicts.probe_types["XCTD-1"]: Dicts.sensor_types["XCTD"],
        Dicts.probe_types["XCTD-2"]: Dicts.sensor_types["XCTD"]
    }

    def __init__(self):
        super(Aoml, self).__init__()
        self.desc = "AOML"
        self._ext.add('txt')

        # header tokens
        self.tk_latitude = 'Latitude'
        self.tk_longitude = 'Longitude'

        # body tokens
        self.tk_depth = 'Depth'
        self.tk_temp = 'Temperature'
        self.tk_speed = 'Sound' # UNUSED for the current format
        self.tk_sal = 'Salinity' # UNUSED for the current format

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """Parsing header: field header, time, latitude, longitude """
        logger.debug('parsing header')

        date_str = ''

        for line in self.lines:
            self.samples_offset += 1
            line = line.strip()

            if line.startswith(self.tk_latitude):  # latitude
                lat_str = line.split('|')[-1].lstrip().strip()
                if len(lat_str) > 0:
                    try:
                        lat_deg = int(line.split()[-3])
                        lat_min = float(line.split()[-2])
                        lat_dir = line.split()[-1]
                        self.ssp.cur.meta.latitude = lat_deg + lat_min / 60.
                        if lat_dir == 'S':
                            self.ssp.cur.meta.latitude *= -1
                    except ValueError:
                        logger.warning('issue in casting the latitude at line #%s' % self.samples_offset)
            elif line.startswith(self.tk_longitude):  # longitude
                lon_str = line.split('|')[-1].lstrip().strip()
                if len(lon_str) > 0:
                    try:
                        lon_deg = int(line.split()[-3])
                        lon_min = float(line.split()[-2])
                        lon_dir = line.split()[-1]
                        self.ssp.cur.meta.longitude = lon_deg + lon_min / 60.
                        if lon_dir == 'W':
                            self.ssp.cur.meta.longitude *= -1
                    except ValueError:
                        logger.warning('issue in casting the longitude at line #%s' % self.samples_offset)
            elif line.startswith('Year'):
                date_str = '%s%s' % (date_str, line.split()[-1])
            elif line.startswith('Month'):
                date_str = '%s %s' % (date_str, line.split()[-1])
            elif line.startswith('Day'):
                date_str = '%s %s' % (date_str, line.split()[-1])
            elif line.startswith('Hour'):
                date_str = '%s %s' % (date_str, line.split()[-1])
            elif line.startswith('Minute'):
                date_str = '%s %s' % (date_str, line.split()[-1])
                if len(date_str) == 16:
                    self.ssp.cur.meta.utc_time = dt.datetime.strptime(date_str, '%Y %m %d %H %M')
                    try:
                        self.ssp.cur.meta.utc_time = dt.datetime.strptime(date_str, '%Y %m %d %H %M')
                    except:
                        logger.warning('issue in casting the time format at line #%s' % self.samples_offset)
                else:
                    logger.warning('issue in casting the time format at or before line #%s' % self.samples_offset)
            elif line.startswith('Ship Name'):
                self.ssp.cur.meta.vessel = line.split('|')[-1].strip()
            elif line.startswith('Probe Serial Number'):
                self.ssp.cur.meta.sn = line.split()[-1]
            elif line.startswith('Instrument Type'):
                match = re.search('Sippican (.*?) \(', line)
                try:
                    self.ssp.cur.meta.probe_type = Dicts.probe_types[match.group(1)]
                    self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]
                except (IndexError, KeyError):
                    self.ssp.cur.meta.probe_type = Dicts.probe_types['Unknown']
                    self.ssp.cur.meta.sensor_type = Dicts.sensor_types['Unknown']
                    logger.warning('reverted to unknown probe type at line #%s' % self.samples_offset)
            elif line.startswith(self.tk_depth): # field headers
                col = 0  # field column           
                for field_type in line.split():
                    self.field_index[field_type] = col
                    col += 1
                break

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample fields
        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)
        # initialize additional fields
        # self.ssp.cur.init_more(self.more_fields)

    def _parse_body(self):
        """Parsing samples: depth, speed, temp"""
        logger.debug('parsing body')
        print(self.field_index)

        count = 0
        for line in self.lines[self.samples_offset:len(self.lines)]:

            # skip empty lines
            if len(line.split()) == 0:
                continue

            data = line.split()
            # depth
            try:
                self.ssp.cur.data.depth[count] = float(data[self.field_index[self.tk_depth]])
            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + count))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + count))
                continue

            # temperature
            try:
                self.ssp.cur.data.temp[count] = float(data[self.field_index[self.tk_temp]])
            except Exception as e:
                logger.debug("issue in reading temperature: %s -> skipping" % e)
                
            # salinity
            try:
                self.ssp.cur.data.sal[count] = float(data[self.field_index[self.tk_sal]])
            except Exception as e:
                pass
                #logger.debug("issue in reading salinity: %s -> skipping" % e)

            # sound speed
            try:
                self.ssp.cur.data.speed[count] = float(data[self.field_index[self.tk_speed]])
            except Exception as e:
                pass
                #logger.debug("issue in reading sound speed: %s -> skipping" % e)

            count += 1

        self.ssp.cur.data_resize(count)

