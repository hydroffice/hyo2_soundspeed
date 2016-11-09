from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import os
import shutil
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

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

    def test_creation_of_Rtofs(self):
        prj = SoundSpeedLibrary(data_folder=self.curdir)
        rtofs = Rtofs(data_folder=prj.data_folder, prj=prj)
        self.assertTrue('rtofs' in rtofs.folder)
        self.assertFalse(rtofs.is_present())
        prj.close()

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
