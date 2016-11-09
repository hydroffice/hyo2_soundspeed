from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hydroffice.soundspeed.base import helper


class TestSoundSpeedBaseHelper(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_creation_of_File_info(self):
        fi = helper.FileInfo(__file__)
        self.assertEqual(fi.path, os.path.abspath(__file__))
        self.assertEqual(fi.basename, os.path.basename(os.path.abspath(__file__)).split('.')[0])
        self.assertEqual(fi.ext, os.path.basename(os.path.abspath(__file__)).split('.')[1])
        self.assertEqual(fi.io, None)

        fi.io = open(__file__)
        self.assertEqual(type(fi.io), file)

    def test_creation_with_File_manager(self):
        fm = helper.FileManager(__file__, b'r')
        self.assertEqual(fm.path, os.path.abspath(__file__))
        self.assertEqual(fm.basename, os.path.basename(os.path.abspath(__file__)).split('.')[0])
        self.assertEqual(fm.ext, os.path.basename(os.path.abspath(__file__)).split('.')[1])
        self.assertNotEqual(fm.io, None)
        self.assertFalse(fm.append_exists)

    def test_append_with_File_manager(self):
        fm = helper.FileManager(__file__, b'a')
        self.assertEqual(fm.path, os.path.abspath(__file__))
        self.assertEqual(fm.basename, os.path.basename(os.path.abspath(__file__)).split('.')[0])
        self.assertEqual(fm.ext, os.path.basename(os.path.abspath(__file__)).split('.')[1])
        self.assertNotEqual(fm.io, None)
        self.assertTrue(fm.append_exists)

    def test_result_from_libs_info(self):
        msg = helper.info_libs().lower()
        # logger.info(msg)
        self.assertTrue('hydroffice' in msg)
        self.assertTrue('pyside' in msg)
        self.assertTrue('gdal' in msg)
        self.assertTrue('pyproj' in msg)
        self.assertTrue('netcdf4' in msg)

    def test_explore_folder_with_fake_path(self):
        self.assertFalse(helper.explore_folder('z:/fake/path'))


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedBaseHelper))
    return s
