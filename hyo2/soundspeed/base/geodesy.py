import math
import logging

import numpy as np

from osgeo import ogr
from osgeo import osr
from pyproj import Geod

from hyo2.abc.lib.gdal_aux import GdalAux

logger = logging.getLogger(__name__)

wkt_3857 = "PROJCS[\"WGS 84 / Pseudo-Mercator\",GEOGCS[\"Popular Visualisation CRS\"," \
           "DATUM[\"Popular_Visualisation_Datum\",SPHEROID[\"Popular Visualisation Sphere\"," \
           "6378137,0,AUTHORITY[\"EPSG\",\"7059\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6055\"]]," \
           "PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.01745329251994328," \
           "AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4055\"]],UNIT[\"metre\",1," \
           "AUTHORITY[\"EPSG\",\"9001\"]],PROJECTION[\"Mercator_1SP\"],PARAMETER[\"central_meridian\",0]," \
           "PARAMETER[\"scale_factor\",1],PARAMETER[\"false_easting\",0],PARAMETER[\"false_northing\",0]," \
           "AUTHORITY[\"EPSG\",\"3785\"],AXIS[\"X\",EAST],AXIS[\"Y\",NORTH]]"


class Geodesy:
    """ A class about geodetic methods and conversions """

    @classmethod
    def radians(cls, degrees=0.0, minutes=0.0, seconds=0.0):
        """ Conversion of degrees, minutes and seconds to radians

        Args:
            degrees:            Degrees
            minutes:            Minutes
            seconds:            Seconds
        """
        toggle = False
        if degrees < 0.0:
            toggle = True
            degrees *= -1.0

        if minutes:
            degrees += minutes / cls._arc_minutes(degrees=1.0)
        if seconds:
            degrees += seconds / cls._arc_seconds(degrees=1.0)

        if toggle:
            degrees *= -1.0

        return math.radians(degrees)

    @classmethod
    def _arc_minutes(cls, degrees=0.0, radians=0.0, arc_seconds=0.0):

        if radians:
            degrees += math.degrees(radians)

        if arc_seconds:
            degrees += arc_seconds / cls._arc_seconds(degrees=1.)

        return degrees * 60.0

    @classmethod
    def _arc_seconds(cls, degrees=0.0, radians=0.0, arc_minutes=0.0):
        """
        TODO docs.
        """

        if radians:
            degrees += math.degrees(radians)

        if arc_minutes:
            degrees += arc_minutes / cls._arc_minutes(degrees=1.0)

        return degrees * 3600.0

    @classmethod
    def degrees(cls, radians):
        """ Radians to degree

        Args:
            radians:        Radians
        """

        return math.degrees(radians)

    @classmethod
    def dms2dd(cls, degrees=0.0, minutes=0.0, seconds=0.0):
        """ Convert degree format from DMS to DD

        Args:
            degrees:        Degrees
            minutes:        Minutes
            seconds:        Seconds
        """

        return cls.degrees(cls.radians(degrees, minutes, seconds))

    @classmethod
    def dd2dms(cls, dd):
        """ Convert degree format from DD to DMS """

        toggle = False
        if dd < 0.0:
            dd *= -1
            toggle = True
        degrees = np.floor(dd)
        m = (dd - np.floor(dd)) * 60.0
        minutes = np.floor(m)
        s = (m - np.floor(m)) * 60.0
        if toggle:
            degrees *= -1.0
        return degrees, minutes, s

    @classmethod
    def dd2dm(cls, dd):
        """ Convert degree format from DD to DM.M

        Args:
            dd:             Decimal degree
        Returns:
            list:           Degrees, Minutes
        """

        toggle = False
        if dd < 0.0:
            dd *= -1
            toggle = True
        degrees = np.floor(dd)
        minutes = (dd - np.floor(dd)) * 60.0

        if toggle:
            degrees *= -1.0
        return degrees, minutes

    @classmethod
    def get_transformed_point(cls, long_in, lat_in, epsg_inputs=4326, epsg_calc=3857):
        """" Perform coordinate pair transformation

        Args:
            long_in:            Input longitude
            lat_in:             Input latitude
            epsg_inputs:        Input EPSG CRS
            epsg_calc:          Output EPSG CRS
        Returns:
            list:               X, Y
        """

        GdalAux.check_gdal_data()

        osr_inputs = osr.SpatialReference()
        osr_inputs.ImportFromEPSG(epsg_inputs)
        osr_calc = osr.SpatialReference()
        if epsg_inputs == 4326:
            osr_calc.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        if epsg_calc == 3857:
            osr_calc.ImportFromWkt(wkt_3857)
        else:
            osr_calc.ImportFromEPSG(epsg_calc)
        coord_transform = osr.CoordinateTransformation(osr_inputs, osr_calc)
        # print(type(coord_transform))

        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(long_in, lat_in)
        point.Transform(coord_transform)

        # print(point)
        return point.GetX(), point.GetY()

    def __init__(self):
        """ Initialization """

        GdalAux.check_gdal_data()
        GdalAux.check_proj4_data()

        self.geo = Geod(ellps='WGS84')

    @classmethod
    def _convert_to_meter(cls, dist, units):
        """ Helper function that converts the distance in various unit of measure """
        if units.lower() == "m":
            return dist
        elif units.lower() == "km":
            return dist * 0.001
        elif units.lower() == "sm":
            # return raw_dist * 0.00062137
            return (dist / 1000) * 0.621371192
        elif units.lower() == "nm":
            # return raw_dist * 0.000539956803
            return (dist / 1000) * 0.539956803
        else:
            raise RuntimeError("Unknown unit: %s" % units)

    @classmethod
    def haversine(cls, long_1, lat_1, long_2, lat_2):
        """ Calculate the great circle distance between two points on a spherical Earth"""
        # convert decimal degrees to radians
        long_1, lat_1, long_2, lat_2 = map(math.radians, [long_1, lat_1, long_2, lat_2])

        dlon = long_2 - long_1
        dlat = lat_2 - lat_1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat_1) * math.cos(lat_2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371000  # Radius of earth in meters. Use 3956 for miles
        return c * r

    def distance(self, long_1, lat_1, long_2, lat_2, units="m"):
        """ Returns distance in 'units' (default m) between two Lat Lon point sets

        Args:
            long_1:             Longitude of point 1
            lat_1:              Latitude of point 1
            long_2:             Longitude of point 2
            lat_2:              Latitude of point 2
            units:              Units (optional) can be "m", "km", "sm", or "nm"
        Returns:
            float:              Distance (in the selected unit of measure)
        """
        try:
            _, _, dist = self.geo.inv(lons1=long_1, lats1=lat_1, lons2=long_2, lats2=lat_2, radians=False)

        except ValueError:
            dist = self.haversine(long_1=long_1, lat_1=lat_1, long_2=long_2, lat_2=lat_2)
            # log.info("%s > switch to Haversine: %s" % (e, dist))

        return self._convert_to_meter(dist=dist, units=units)

    def forward(self, long_1, lat_1, bearing, dist, units="m"):
        """ Returns forward point in 'units' (default m) based on bearing and range in km

        Args:
            long_1:             Longitude of starting point
            lat_1:              Latitude of starting point
            bearing:            Bearing
            dist:               Distance
            units:              Units (optional) can be "m", "km", "sm", or "nm"
        Returns:
            list:               Longitude and latitude for the forward point
        """
        distance = self._convert_to_meter(dist, units)

        long_2, lat_2, _ = self.geo.fwd(lons=long_1, lats=lat_1, az=bearing, dist=distance, radians=False)

        return long_2, lat_2


utm_zone2epsg = {
    # north
    "1N": 32601,
    "2N": 32602,
    "3N": 32603,
    "4N": 32604,
    "5N": 32605,
    "6N": 32606,
    "7N": 32607,
    "8N": 32608,
    "9N": 32609,
    "10N": 32610,
    "11N": 32611,
    "12N": 32612,
    "13N": 32613,
    "14N": 32614,
    "15N": 32615,
    "16N": 32616,
    "17N": 32617,
    "18N": 32618,
    "19N": 32619,
    "20N": 32620,
    "21N": 32621,
    "22N": 32622,
    "23N": 32623,
    "24N": 32624,
    "25N": 32625,
    "26N": 32626,
    "27N": 32627,
    "28N": 32628,
    "29N": 32629,
    "30N": 32630,
    "31N": 32631,
    "32N": 32632,
    "33N": 32633,
    "34N": 32634,
    "35N": 32635,
    "36N": 32636,
    "37N": 32637,
    "38N": 32638,
    "39N": 32639,
    "40N": 32640,
    "41N": 32641,
    "42N": 32642,
    "43N": 32643,
    "44N": 32644,
    "45N": 32645,
    "46N": 32646,
    "47N": 32647,
    "48N": 32648,
    "49N": 32649,
    "50N": 32650,
    "51N": 32651,
    "52N": 32652,
    "53N": 32653,
    "54N": 32654,
    "55N": 32655,
    "56N": 32656,
    "57N": 32657,
    "58N": 32658,
    "59N": 32659,
    "60N": 32660,
    # south
    "1S": 32701,
    "2S": 32702,
    "3S": 32703,
    "4S": 32704,
    "5S": 32705,
    "6S": 32706,
    "7S": 32707,
    "8S": 32708,
    "9S": 32709,
    "10S": 32710,
    "11S": 32711,
    "12S": 32712,
    "13S": 32713,
    "14S": 32714,
    "15S": 32715,
    "16S": 32716,
    "17S": 32717,
    "18S": 32718,
    "19S": 32719,
    "20S": 32720,
    "21S": 32721,
    "22S": 32722,
    "23S": 32723,
    "24S": 32724,
    "25S": 32725,
    "26S": 32726,
    "27S": 32727,
    "28S": 32728,
    "29S": 32729,
    "30S": 32730,
    "31S": 32731,
    "32S": 32732,
    "33S": 32733,
    "34S": 32734,
    "35S": 32735,
    "36S": 32736,
    "37S": 32737,
    "38S": 32738,
    "39S": 32739,
    "40S": 32740,
    "41S": 32741,
    "42S": 32742,
    "43S": 32743,
    "44S": 32744,
    "45S": 32745,
    "46S": 32746,
    "47S": 32747,
    "48S": 32748,
    "49S": 32749,
    "50S": 32750,
    "51S": 32751,
    "52S": 32752,
    "53S": 32753,
    "54S": 32754,
    "55S": 32755,
    "56S": 32756,
    "57S": 32757,
    "58S": 32758,
    "59S": 32759,
    "60S": 32760,
}
