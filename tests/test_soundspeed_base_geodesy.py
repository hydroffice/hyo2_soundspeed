# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import sys
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hydroffice.soundspeed.base.geodesy import Geodesy

from osgeo import gdal


class TestSoundSpeedGeodesy(unittest.TestCase):

    gdal_version = int(gdal.__version__.split('.')[0])
    is_windows = sys.platform.startswith("win")

    def setUp(self):
        # data source:
        # > http://www.movable-type.co.uk/scripts/latlong.html
        # > http://www.rapidtables.com/convert/number/degrees-to-radians.htm
        #
        # data:
        # - starting point: 53°19′14″N / 001°43′47″W >>> 53.320556, 1.729722
        # - bearing: 096°01′18″
        # - distance: 124.8 km

        self.trusted_long_1_d = -1
        self.trusted_long_1_m = 43
        self.trusted_long_1_s = 47
        self.trusted_long_1 = -1.729722
        self.trusted_lat_1_d = 53
        self.trusted_lat_1_m = 19
        self.trusted_lat_1_s = 14
        self.trusted_lat_1 = 53.320556
        self.trusted_bearing = 96.021667
        self.trusted_long_1_rad = -0.030189344044
        self.trusted_lat_1_rad = 0.93061926119
        self.trusted_bearing_rad = 1.6758942424

    def tearDown(self):
        pass

    def test_radians(self):
        self.assertAlmostEqual(Geodesy.radians(degrees=self.trusted_long_1_d,
                                               minutes=self.trusted_long_1_m,
                                               seconds=self.trusted_long_1_s),
                               self.trusted_long_1_rad)

        self.assertAlmostEqual(Geodesy.radians(degrees=self.trusted_lat_1_d,
                                               minutes=self.trusted_lat_1_m,
                                               seconds=self.trusted_lat_1_s),
                               self.trusted_lat_1_rad)

        self.assertAlmostEqual(Geodesy.radians(degrees=self.trusted_bearing),
                               self.trusted_bearing_rad)

    def test_degree(self):
        self.assertAlmostEqual(Geodesy.degrees(radians=self.trusted_long_1_rad),
                               self.trusted_long_1)

        self.assertAlmostEqual(Geodesy.degrees(radians=self.trusted_lat_1_rad),
                               self.trusted_lat_1)

        self.assertAlmostEqual(Geodesy.degrees(radians=self.trusted_bearing_rad),
                               self.trusted_bearing)

    def test_dms2dd(self):
        self.assertAlmostEqual(Geodesy.dms2dd(degrees=self.trusted_long_1_d,
                                               minutes=self.trusted_long_1_m,
                                               seconds=self.trusted_long_1_s),
                               self.trusted_long_1, places=6)

        self.assertAlmostEqual(Geodesy.dms2dd(degrees=self.trusted_long_1_d,
                                               minutes=self.trusted_long_1_m,
                                               seconds=self.trusted_long_1_s),
                               self.trusted_long_1, places=6)

    def test_dd2dms(self):
        d, m, s = Geodesy.dd2dms(self.trusted_long_1)
        self.assertAlmostEqual(d, self.trusted_long_1_d, places=6)
        self.assertAlmostEqual(m, self.trusted_long_1_m, places=6)
        self.assertAlmostEqual(round(s), self.trusted_long_1_s)

        d, m, s = Geodesy.dd2dms(self.trusted_lat_1)
        self.assertAlmostEqual(d, self.trusted_lat_1_d, places=6)
        self.assertAlmostEqual(m, self.trusted_lat_1_m, places=6)
        self.assertAlmostEqual(round(s), self.trusted_lat_1_s)

    def test_convert_to_meter(self):
        self.assertEqual(Geodesy._convert_to_meter(1, "m"), 1)
        self.assertAlmostEqual(Geodesy._convert_to_meter(1, "km"), 0.001)
        self.assertAlmostEqual(Geodesy._convert_to_meter(1, "sm"), 0.000621371)
        self.assertAlmostEqual(Geodesy._convert_to_meter(1, "nm"), 0.000539957)

    def test_haversine(self):
        dist = Geodesy.haversine(long_1=-70.9395, lat_1=43.13555, long_2=14.9, lat_2=36.783333)
        self.assertTrue((dist - 7020851.6) < 0.1)

    def test_distance(self):
                # data retrieved from: http://geographiclib.sourceforge.net/cgi-bin/GeodSolve
        # ref: C. F. F. Karney, Algorithms for geodesics, J. Geodesy 87, 43–55 (2013); DOI: 10.1007/s00190-012-0578-z
        long_1 = -70.9395
        lat_1 = 43.13555
        long_2 = 14.9
        lat_2 = 36.783333

        g = Geodesy()
        dist = g.distance(long_1=long_1, lat_1=lat_1, long_2=long_2, lat_2=lat_2)
        self.assertTrue((dist - 7037989.518) < 0.001)

    @unittest.skipUnless(is_windows and (gdal_version == 1), "only GDAL 1.x on Windows")
    def test_forward(self):
        # data retrieved from: http://geographiclib.sourceforge.net/cgi-bin/GeodSolve
        # ref: C. F. F. Karney, Algorithms for geodesics, J. Geodesy 87, 43–55 (2013); DOI: 10.1007/s00190-012-0578-z
        long_1 = -70.9395
        lat_1 = 43.13555
        long_2 = 14.9
        lat_2 = 36.783333
        az_1 = 63.52826597
        distance = 7037989.518

        g = Geodesy()
        long_2_calc, lat_2_calc = g.forward(long_1=long_1, lat_1=lat_1, bearing=az_1, dist=distance, units='m')
        self.assertAlmostEqual(long_2_calc, long_2)
        self.assertAlmostEqual(lat_2_calc, lat_2)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedGeodesy))
    return s
