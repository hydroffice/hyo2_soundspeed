import unittest
import os
import shutil

from hyo2.soundspeedmanager import AppInfo
from hyo2.soundspeed.atlas import atlases
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary


class TestSoundSpeedAtlasAtlases(unittest.TestCase):

    def setUp(self):
        self.cur_dir = os.path.abspath(os.path.dirname(__file__))

    def tearDown(self):
        dir_items = os.listdir(self.cur_dir)
        for item in dir_items:
            if item.split('.')[-1] == 'db':
                os.remove(os.path.join(self.cur_dir, item))
            if item == 'atlases':
                shutil.rmtree(os.path.join(self.cur_dir, item))

    def test_creation_of_Atlases(self):
        lib = SoundSpeedLibrary(data_folder=self.cur_dir)
        atl = atlases.Atlases(prj=lib)

        self.assertTrue("atlases" in atl.rtofs_folder)
        self.assertTrue("woa" in atl.woa09_folder)
        self.assertTrue("woa" in atl.woa13_folder)
        self.assertTrue("woa" in atl.woa18_folder)

        lib.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedAtlasAtlases))
    return s
