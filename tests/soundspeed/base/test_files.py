import unittest
import os
from io import IOBase

from hyo2.ssm2.app.gui.soundspeedmanager import app_info
from hyo2.ssm2.lib.base import files


class TestSoundSpeedBaseFiles(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_creation_of_File_info(self):
        fi = files.FileInfo(__file__)
        self.assertEqual(fi.path, os.path.abspath(__file__))
        self.assertEqual(fi.basename, os.path.basename(os.path.abspath(__file__)).split('.')[0])
        self.assertEqual(fi.ext, os.path.basename(os.path.abspath(__file__)).split('.')[1])
        self.assertEqual(fi.io, None)

        fi.io = open(__file__)
        self.assertTrue(isinstance(fi.io, IOBase))

    def test_creation_with_File_manager(self):
        fm = files.FileManager(__file__, 'r')
        self.assertEqual(fm.path, os.path.abspath(__file__))
        self.assertEqual(fm.basename, os.path.basename(os.path.abspath(__file__)).split('.')[0])
        self.assertEqual(fm.ext, os.path.basename(os.path.abspath(__file__)).split('.')[1])
        self.assertNotEqual(fm.io, None)
        self.assertFalse(fm.append_exists)

    def test_append_with_File_manager(self):
        fm = files.FileManager(__file__, 'a')
        self.assertEqual(fm.path, os.path.abspath(__file__))
        self.assertEqual(fm.basename, os.path.basename(os.path.abspath(__file__)).split('.')[0])
        self.assertEqual(fm.ext, os.path.basename(os.path.abspath(__file__)).split('.')[1])
        self.assertNotEqual(fm.io, None)
        self.assertTrue(fm.append_exists)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedBaseFiles))
    return s
