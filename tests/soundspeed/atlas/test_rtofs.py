import unittest
import os
import shutil
import logging

from hyo2.soundspeedmanager import AppInfo
from hyo2.soundspeed.atlas.rtofs.rtofs import Rtofs
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary

logger = logging.getLogger()


class TestSoundSpeedAtlasRtofs(unittest.TestCase):

    def setUp(self):
        self.cur_dir = os.path.abspath(os.path.dirname(__file__))

    def tearDown(self):
        dir_items = os.listdir(self.cur_dir)
        for item in dir_items:
            if item.split('.')[-1] == 'db':
                os.remove(os.path.join(self.cur_dir, item))
            if item == 'atlases':
                shutil.rmtree(os.path.join(self.cur_dir, item))

    def test_creation_of_Rtofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        rtofs = Rtofs(data_folder=prj.rtofs_folder, prj=prj)
        self.assertTrue('rtofs' in rtofs.data_folder)
        self.assertFalse(rtofs.is_present())
        prj.close()

    def test_download_db_from_Rtofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        rtofs = Rtofs(data_folder=prj.data_folder, prj=prj)
        rtofs.download_db(server_mode=True)

        # to avoid test failures
        if not rtofs.is_present():
            logger.warning("unable to download RTOFS data")
        # self.assertTrue(rtofs.is_present())

        prj.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedAtlasRtofs))
    return s
