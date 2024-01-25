import re
import datetime as dt
import logging

logger = logging.getLogger(__name__)

from hyo2.ssm2.lib.formats.readers.abstract import AbstractTextReader
from hyo2.ssm2.lib.profile.dicts import Dicts
from hyo2.ssm2.lib.base.callbacks.cli_callbacks import CliCallbacks


class CSIRO_DTC(AbstractTextReader):
    """CSIRO Deep Toad Camera"""

    def __init__(self):
        super(CSIRO_DTC, self).__init__()
        self.desc = "CSIRO DTC"
        self._ext.add('json')

        self.data_regex = r'^.*\{\"message\": \"dtc\.sbe37\.ctd\.eng\".+sea_water_temperature_celsius\": \"' \
                     r'(?P<temp>\d+\.\d+)\".+sea_water_pressure\": \"' \
                     r'(?P<pressure>\d+\.\d+)\".+sea_water_practical_salinity\": \"' \
                     r'(?P<salinity>\d+\.\d+).+speed_of_sound_in_sea_water\": \"' \
                     r'(?P<soundspeed>\d+\.\d+)\".+timestamp\": \"(?P<timestamp>.+Z)\".+$'

        self.position_regex = r'^.*\{\"message\": \"investigator\.seapath\.gps\.eng\".+vessel_latitude\": \"' \
                              r'(?P<lat>\d+\.\d+)\".+vessel_latitude_indicator\": \"' \
                              r'(?P<lat_sign>\D)\".+vessel_longitude\": \"' \
                              r'(?P<long>\d+\.\d+)\".+vessel_longitude_indicator\": \"(?P<long_sign>\D)\".+$'

        self.metadata_regex = r'^.*\{\"message\": \"dtc.deployment.metadata".+vessel\": \"' \
                              r'(?P<vessel>[^\"]+)\".+voyage_identifier\": \"(?P<voyage_id>[^\"]+)\".+$'

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
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
        """Parsing header: field header, time, latitude, longitude"""
        logger.debug('parsing header')
        first_timestamp_search = None #Initilise to None, ie not found
        first_position_search = None
        metadata_search = None

        try:
            for line in self.lines:
                #Get just the first occurance of a timestamp from CTD data
                if not first_timestamp_search: #We've already found a timestamp (but not position, so we're still in the loop)
                    first_timestamp_search = re.search(self.data_regex, line)
                if first_timestamp_search:
                    first_timestamp = dt.datetime.strptime(first_timestamp_search.group('timestamp'), "%Y-%m-%dT%H:%M:%S.%fZ") #eg 2022-10-15T08:10:58.411Z
                    self.ssp.cur.meta.utc_time = dt.datetime(year=first_timestamp.year, month=first_timestamp.month, day=first_timestamp.day,
                                                    hour=first_timestamp.hour, minute=first_timestamp.minute, second=first_timestamp.second)
                #Get first valid position
                if not first_position_search: #We've already found a position (but not timestamp, so we're still in the loop)
                    first_position_search = re.search(self.position_regex, line)
                if first_position_search:
                    latitude = first_position_search.group('lat')
                    longitude = first_position_search.group('long')
                    if first_position_search.group('lat_sign') == 'S':
                        latitude = '-{}'.format(latitude) #Prepend negative if we're south
                    if first_position_search.group('long_sign') == 'W':
                        longitude = '-{}'.format(longitude)  # Prepend negative if we're west
                    self.ssp.cur.meta.latitude = float(latitude)
                    self.ssp.cur.meta.longitude = float(longitude)

                if not metadata_search:
                    metadata_search = re.search(self.metadata_regex, line)
                if metadata_search:
                    self.ssp.cur.meta.survey = metadata_search.group('voyage_id')
                    self.ssp.cur.meta.vessel = metadata_search.group('vessel')

                if first_timestamp_search and first_position_search and metadata_search: #We've extracted the data, exit loop to avoid scanning entire file
                    break
        except ValueError as e:
            logger.info("unable to parse timestamp, lat and long: %s" % (e))

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

            data = re.search(self.data_regex, line)

            # skip non-matching lines
            if not data:
                continue

            try:
                self.ssp.cur.data.pressure[count] = float(data.group('pressure'))
                self.ssp.cur.data.speed[count] = float(data.group('soundspeed'))
                self.ssp.cur.data.sal[count] = float(data.group('salinity'))
                self.ssp.cur.data.temp[count] = float(data.group('temp'))

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + count))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + count))
                continue

            count += 1

        self.ssp.cur.data_resize(count)
