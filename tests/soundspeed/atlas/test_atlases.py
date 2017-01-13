from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import os
import shutil

from hydroffice.soundspeed.atlas import atlases
from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary


class TestSoundSpeedAtlasAtlases(unittest.TestCase):

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
    def test_creation_of_Atlases(self):
        lib = SoundSpeedLibrary(data_folder=self.curdir)
        atl = atlases.Atlases(prj=lib)

        self.assertTrue("atlases" in atl.rtofs_folder)
        self.assertTrue("woa" in atl.woa09_folder)
        self.assertTrue("woa" in atl.woa13_folder)

        lib.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedAtlasAtlases))
    return s
