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

from hydroffice.soundspeed.base.callbacks import TestCallbacks


class TestSoundSpeedTestCallbacks(unittest.TestCase):

    def setUp(self):
        self.cb = TestCallbacks()

    def tearDown(self):
        pass

    def test_ask_date(self):
        from datetime import datetime as dt
        self.assertEqual(self.cb.ask_date(), dt.utcnow())

    def test_ask_location(self):
        loc = self.cb.ask_location()
        self.assertGreater(loc[0], 40.)
        self.assertGreater(loc[1], -80.)

    def test_ask_location_from_sis(self):
        self.assertTrue(self.cb.ask_location_from_sis())

    def test_ask_tss(self):
        self.assertEqual(self.cb.ask_tss(), 1500.)

    def test_ask_draft(self):
        self.assertEqual(self.cb.ask_draft(), 8.)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedTestCallbacks))
    return s
