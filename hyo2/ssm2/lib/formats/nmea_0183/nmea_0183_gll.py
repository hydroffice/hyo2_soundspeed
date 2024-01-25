import logging
from typing import Optional
from hyo2.ssm2.lib.formats.nmea_0183.nmea_0183_nav_abstract import Nmea0183NavAbstract

logger = logging.getLogger(__name__)


class Nmea0183GLL(Nmea0183NavAbstract):

    def __init__(self, data: str) -> None:
        super(Nmea0183GLL, self).__init__(data)

        self._lat = Optional[str]
        self._lat_dir = Optional[str]
        self._lon = Optional[str]
        self._lon_dir = Optional[str]
        self._timestamp = Optional[str]
        self._status = Optional[str]

    def _parse(self) -> None:

        self._lat = self.msg[1]
        self._lat_dir = self.msg[2]
        self._lon = self.msg[3]
        self._lon_dir = self.msg[4]
        self._timestamp = self.msg[5]
        self._status = self.msg[6]

        try:
            self._latitude = int(self._lat[:2]) + float(self._lat[2:]) / 60.
            if self._lat_dir == 'S':
                self._latitude = -1.0 * self.latitude
            # logger.debug("NMEA 0183 $$GLL lat: {}".format(self.latitude))

        except Exception as e:
            logger.warning("unable to interpret latitude from %s and %s: %s" % (self._lat, self._lat_dir, e))

        try:
            self._longitude = int(self._lon[:3]) + float(self._lon[3:]) / 60.
            if self._lon_dir == 'W':
                self._longitude = -1.0 * self.longitude
            # logger.debug("NMEA 0183 $$GLL lon: {}".format(self.longitude))

        except Exception as e:
            logger.warning("unable to interpret longitude from %s and %s: %s" % (self._lon, self._lon_dir, e))
