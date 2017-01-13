from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import os
import shutil

from hydroffice.soundspeed.atlas.rtofs.rtofs import Rtofs
from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary


class TestSoundSpeedAtlasRtofs(unittest.TestCase):

    def setUp(self):
        self.curdir = os.path.abspath(os.path.dirname(__file__))

    def tearDown(self):
        dir_items = os.listdir(self.curdir)
        for item in dir_items:
            if item.split('.')[-1] == 'db':
                os.remove(os.path.join(self.curdir, item))
            if item == 'atlases':
                shutil.rmtree(os.path.join(self.curdir, item))

    @unittest.expectedFailure
    def test_creation_of_Rtofs(self):
        prj = SoundSpeedLibrary(data_folder=self.curdir)
        rtofs = Rtofs(data_folder=prj.data_folder, prj=prj)
        self.assertTrue('rtofs' in rtofs.folder)
        self.assertFalse(rtofs.is_present())
        prj.close()

    @unittest.expectedFailure
    def test_download_db_from_Rtofs(self):
        prj = SoundSpeedLibrary(data_folder=self.curdir)
        rtofs = Rtofs(data_folder=prj.data_folder, prj=prj)
        rtofs.download_db(server_mode=True)
        self.assertTrue(rtofs.is_present())
        prj.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedAtlasRtofs))
    return s
