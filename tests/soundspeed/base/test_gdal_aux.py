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

from hydroffice.soundspeed.base.gdal_aux import GdalAux

from osgeo import gdal


class TestSoundSpeedGdalAux(unittest.TestCase):

    gdal_version = int(gdal.__version__.split('.')[0])
    is_windows = sys.platform.startswith("win")

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skipUnless(is_windows, "only on Windows")
    def test_list_ogr_drivers(self):
        GdalAux.list_ogr_drivers()

    @unittest.skipUnless(is_windows, "only on Windows")
    def test_current_gdal_version(self):
        version = GdalAux.current_gdal_version()

        self.assertEqual(type(version), int)

    @unittest.skipUnless(is_windows, "only on Windows")
    def test_is_gdal_2(self):
        flag = GdalAux.is_gdal_2()

        self.assertEqual(type(flag), bool)

    @unittest.skipUnless(is_windows, "only on Windows")
    def test_push_gdal_error_handler(self):
        GdalAux.push_gdal_error_handler()

        self.assertTrue(GdalAux.error_loaded)

    @unittest.skipUnless(is_windows, "only on Windows")
    def test_check_gdal_data(self):
        GdalAux.check_gdal_data()

        self.assertTrue(GdalAux.data_fixed)
        self.assertTrue(GdalAux.error_loaded)

    @unittest.skipUnless(is_windows, "only on Windows")
    def test_use_of_Gdal_aux(self):
        aux = GdalAux()

        for fmt in aux.ogr_formats:

            # get a driver
            drv = aux.get_ogr_driver(GdalAux.ogr_formats[fmt])
            self.assertEqual(drv.name, fmt)

            # create a file
            data_folder = os.path.abspath(os.curdir)
            output_path = os.path.join(data_folder, 'dummy')
            src = aux.create_ogr_data_source(ogr_format=GdalAux.ogr_formats[fmt], output_path=output_path)
            self.assertNotEqual(src, None)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedGdalAux))
    return s
