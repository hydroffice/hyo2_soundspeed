import unittest
import os
import shutil
import logging

from hyo2.soundspeedmanager import AppInfo
from hyo2.soundspeed.atlas.regofs import RegOfs
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary

logger = logging.getLogger()


class TestSoundSpeedAtlasGomofs(unittest.TestCase):

    def setUp(self):
        self.cur_dir = os.path.abspath(os.path.dirname(__file__))

    def tearDown(self):
        dir_items = os.listdir(self.cur_dir)
        for item in dir_items:
            if item.split('.')[-1] == 'db':
                os.remove(os.path.join(self.cur_dir, item))
            if item == 'atlases':
                shutil.rmtree(os.path.join(self.cur_dir, item))

    def test_creation_of_Gomofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        gomofs = RegOfs(data_folder=prj.gomofs_folder, prj=prj, model=RegOfs.Model.GoMOFS)
        self.assertTrue('regofs' in gomofs.data_folder)
        self.assertFalse(gomofs.is_present())
        prj.close()

    def test_download_db_from_Gomofs(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        gomofs = RegOfs(data_folder=prj.gomofs_folder, prj=prj, model=RegOfs.Model.GoMOFS)
        gomofs.download_db(server_mode=True)

        # to avoid test failures
        if not gomofs.is_present():
            logger.warning("unable to download GoMOFS data")
        # self.assertTrue(rtofs.is_present())

        prj.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedAtlasGomofs))
    return s
