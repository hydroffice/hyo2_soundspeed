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

from hydroffice.soundspeed.atlas import atlases
from hydroffice.soundspeed.project import Project


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

    def test_creation_of_Atlases(self):
        prj = Project(data_folder=self.curdir)
        atl = atlases.Atlases(prj=prj)

        self.assertTrue("atlases" in atl.rtofs_folder)
        self.assertTrue("woa" in atl.woa09_folder)
        self.assertTrue("woa" in atl.woa13_folder)

        prj.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedAtlasAtlases))
    return s
