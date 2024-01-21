import logging
from hyo2.soundspeed.formats.nmea_0183.nmea_0183_nav_abstract import Nmea0183NavAbstract

logger = logging.getLogger(__name__)


class Nmea0183GGA(Nmea0183NavAbstract):

    def __init__(self, data: str) -> None:
        super(Nmea0183GGA, self).__init__(data)

    def _parse(self) -> None:

        self._timestamp = self.msg[1]
        self._lat = self.msg[2]
        self._lat_dir = self.msg[3]
        self._lon = self.msg[4]
        self._lon_dir = self.msg[5]
        self._gps_qual = self.msg[6]
        self._num_sats = self.msg[7]
        self._horizontal_dil = self.msg[8]
        self._altitude = self.msg[9]
        self._altitude_units = self.msg[10]
        self._geo_sep = self.msg[11]
        self._geo_sep_units = self.msg[12]
        self._age_gps_data = self.msg[13]
        self._ref_station_id = self.msg[14]

        try:
            self._latitude = int(self._lat[:2]) + float(self._lat[2:]) / 60.
            if self._lat_dir == 'S':
                self._latitude = -1.0 * self.latitude
            # logger.debug("NMEA 0183 $$GGA lat: {}".format(self.latitude))

        except Exception as e:
            logger.warning("unable to interpret latitude from %s and %s: %s" % (self._lat, self._lat_dir, e))

        try:
            self._longitude = int(self._lon[:3]) + float(self._lon[3:]) / 60.
            if self._lon_dir == 'W':
                self._longitude = -1.0 * self.longitude
            # logger.debug("NMEA 0183 $$GGA lon: {}".format(self.longitude))

        except Exception as e:
            logger.warning("unable to interpret longitude from %s and %s: %s" % (self._lon, self._lon_dir, e))
