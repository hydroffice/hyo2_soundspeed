from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hydroffice.soundspeed.base.settings import Settings


class TestSoundSpeedSettings(unittest.TestCase):

    def setUp(self):
        self.data_folder = os.path.abspath(os.curdir)
        self.db_name = "settings.db"
        self.db_path = os.path.join(self.data_folder, self.db_name)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_create_settings_and_check_db_path(self):
        settings = Settings(self.data_folder)
        db = settings.db
        self.assertEqual(db.db_path, self.db_path)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedSettings))
    return s
