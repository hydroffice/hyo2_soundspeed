import unittest
import os
from io import IOBase

from hyo2.soundspeed.base import helper


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
        self.assertTrue(isinstance(fi.io, IOBase))

    def test_creation_with_File_manager(self):
        fm = helper.FileManager(__file__, 'r')
        self.assertEqual(fm.path, os.path.abspath(__file__))
        self.assertEqual(fm.basename, os.path.basename(os.path.abspath(__file__)).split('.')[0])
        self.assertEqual(fm.ext, os.path.basename(os.path.abspath(__file__)).split('.')[1])
        self.assertNotEqual(fm.io, None)
        self.assertFalse(fm.append_exists)

    def test_append_with_File_manager(self):
        fm = helper.FileManager(__file__, 'a')
        self.assertEqual(fm.path, os.path.abspath(__file__))
        self.assertEqual(fm.basename, os.path.basename(os.path.abspath(__file__)).split('.')[0])
        self.assertEqual(fm.ext, os.path.basename(os.path.abspath(__file__)).split('.')[1])
        self.assertNotEqual(fm.io, None)
        self.assertTrue(fm.append_exists)

    def test_result_from_libs_info(self):
        msg = helper.info_libs().lower()
        # logger.info(msg)
        self.assertTrue('hyo' in msg)
        self.assertTrue('pyside' in msg)
        self.assertTrue('gdal' in msg)
        self.assertTrue('pyproj' in msg)
        self.assertTrue('netcdf4' in msg)

    def test_explore_folder_with_fake_path(self):
        self.assertFalse(helper.explore_folder('z:/fake/path'))

    def test_first_match(self):

        # fake dict
        a_dict = {
            "a": 1,
            "b": 99,
            "c": 1,
        }

        # test if it gives back the first matching key
        self.assertEqual(helper.first_match(a_dict, 1), "a")

        # test if it raises with a not-existing value
        with self.assertRaises(RuntimeError):
            helper.first_match(a_dict, 2)

    def test_python_path(self):
        self.assertTrue(os.path.exists(helper.python_path()))

    def test_is_pydro(self):
        self.assertEqual(type(helper.is_pydro()), bool)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedBaseHelper))
    return s
