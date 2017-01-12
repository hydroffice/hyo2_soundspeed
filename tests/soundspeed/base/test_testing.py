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

from hydroffice.soundspeed.base import testing


class TestSoundSpeedBaseHelper(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_root_data_folder(self):
        self.assertTrue(os.path.exists(testing.root_data_folder()))

    def test_input_data_folder(self):
        self.assertTrue(os.path.exists(testing.input_data_folder()))

    def test_input_data_sub_folders(self):
        self.assertGreater(len(testing.input_data_sub_folders()), 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedBaseHelper))
    return s
