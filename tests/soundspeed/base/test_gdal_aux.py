import unittest
import sys
import os

from hyo.soundspeed.base.gdal_aux import GdalAux

from osgeo import gdal


class TestSoundSpeedGdalAux(unittest.TestCase):

    gdal_version = int(gdal.__version__.split('.')[0])
    is_windows = sys.platform.startswith("win")

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_list_ogr_drivers(self):
        GdalAux.list_ogr_drivers()

    def test_current_gdal_version(self):
        version = GdalAux.current_gdal_version()

        self.assertEqual(type(version), int)

    def test_is_gdal_2(self):
        flag = GdalAux.is_gdal_2()

        self.assertEqual(type(flag), bool)

    def test_push_gdal_error_handler(self):
        GdalAux.push_gdal_error_handler()

        self.assertTrue(GdalAux.error_loaded)

    def test_check_gdal_data(self):
        GdalAux.check_gdal_data()

        self.assertTrue(GdalAux.gdal_data_fixed)
        self.assertTrue(GdalAux.error_loaded)

    def test_check_proj4_data(self):
        GdalAux.check_proj4_data()

        self.assertTrue(GdalAux.proj4_data_fixed)

    def test_use_of_Gdal_aux(self):
        from hyo.soundspeed.base.testing import output_data_folder

        aux = GdalAux()

        for fmt in aux.ogr_formats:

            # get a driver
            drv = aux.get_ogr_driver(GdalAux.ogr_formats[fmt])
            self.assertEqual(drv.name, fmt)

            # create a file
            output_path = os.path.join(output_data_folder(), 'test_gdal_aux')
            src = aux.create_ogr_data_source(ogr_format=GdalAux.ogr_formats[fmt], output_path=output_path)
            self.assertNotEqual(src, None)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedGdalAux))
    return s
