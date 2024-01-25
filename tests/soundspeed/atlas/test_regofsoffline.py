import unittest
import os
import shutil
import logging

from hyo2.ssm2.app.gui.soundspeedmanager import AppInfo
from hyo2.ssm2.lib.atlas.regofsoffline import RegOfsOffline
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger()


class TestSoundSpeedAtlasRegofsOffline(unittest.TestCase):

    def setUp(self):
        self.cur_dir = os.path.abspath(os.path.dirname(__file__))

    def test_init(self):
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        _ = RegOfsOffline(data_folder=prj.regofs_folder, prj=prj)
        prj.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedAtlasRegofsOffline))
    return s
