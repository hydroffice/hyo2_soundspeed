from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import os
from hydroffice.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hydroffice.soundspeed.base import testing


class TestSoundSpeedFormats(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read_and_write(self):
        self.assertTrue(os.path.exists(testing.root_data_folder()))


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedFormats))
    return s
