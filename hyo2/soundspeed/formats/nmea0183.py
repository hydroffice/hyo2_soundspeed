import logging

logger = logging.getLogger(__name__)


class Nmea0183Nav:

    def __init__(self, data):

        self.data = data
        self.msg = None
        
        self.latitude = None
        self.longitude = None
        
        self.parse()

    def parse(self) -> None:
        self.msg = self.data.split(',')

    def __str__(self):
        return "Latitude: {0}, Longitude: {1}\n".format(self.latitude, self.longitude)


    
class Nmea0183GGA(Nmea0183Nav):

    def __init__(self, data):
        super(Nmea0183GGA, self).__init__(data)

        self.timestamp = self.msg[1]
        self.lat = self.msg[2]
        self.lat_dir = self.msg[3]
        self.lon = self.msg[4]
        self.lon_dir = self.msg[5]
        self.gps_qual = self.msg[6]
        self.num_sats = self.msg[7]
        self.horizontal_dil = self.msg[8]
        self.altitude = self.msg[9]
        self.altitude_units = self.msg[10]
        self.geo_sep = self.msg[11]
        self.geo_sep_units = self.msg[12]
        self.age_gps_data = self.msg[13]
        self.ref_station_id = self.msg[14]

        try:
            self.latitude = int(self.lat[:2]) + float(self.lat[2:])/60.
            if self.lat_dir == 'S':
                self.latitude = -1.0 * self.latitude
            #logger.debug("NMEA-0183 $$GGA lat: {}".format(self.latitude))
        except Exception as e:
            logger.warning("unable to interpret latitude from {0} and {1}, {2}".format(self.lat, self.lat_dir, e))

        try:
            self.longitude = int(self.lon[:3]) + float(self.lon[3:])/60.
            if self.lon_dir == 'W':
                self.longitude = -1.0 * self.longitude
            #logger.debug("NMEA-0183 $$GGA lon: {}".format(self.longitude))
        except Exception as e:
            logger.warning("unable to interpret longitude from {0} and {1}, {2}".format(self.lon, self.lon_dir, e))



    
class Nmea0183GLL(Nmea0183Nav):

    def __init__(self, data):
        super(Nmea0183GLL, self).__init__(data)

        self.msg = self.data.split(',')

        self.lat = self.msg[1]
        self.lat_dir = self.msg[2]
        self.lon = self.msg[3]
        self.lon_dir = self.msg[4]
        self.timestamp = self.msg[5]
        self.status = self.msg[6]

        try:
            self.latitude = int(self.lat[:2]) + float(self.lat[2:])/60.
            if self.lat_dir == 'S':
                self.latitude = -1.0 * self.latitude
            #logger.debug("NMEA-0183 $$GLL lat: {}".format(self.latitude))
        except Exception as e:
            logger.warning("unable to interpret latitude from {0} and {1}, {2}".format(self.lat, self.lat_dir, e))

        try:
            self.longitude = int(self.lon[:3]) + float(self.lon[3:])/60.
            if self.lon_dir == 'W':
                self.longitude = -1.0 * self.longitude
            #logger.debug("NMEA-0183 $$GLL lon: {}".format(self.longitude))
        except Exception as e:
            logger.warning("unable to interpret longitude from {0} and {1}, {2}".format(self.lon, self.lon_dir, e))
            
