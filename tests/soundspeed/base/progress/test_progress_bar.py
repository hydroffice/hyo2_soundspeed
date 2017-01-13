from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import os
import sys
from hydroffice.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hydroffice.soundspeed.base.progress.cli_progress import CliProgress


class TestSoundSpeedTestCliProgress(unittest.TestCase):

    def setUp(self):
        self.progress = CliProgress()
        sys.stdout = None

    def tearDown(self):
        pass

    def test_start_minimal(self):
        try:
            self.progress.start()
        except Exception as e:
            self.fail(e)

    def test_start_custom_title_text(self):
        try:
            self.progress.start(title='Test Bar', text='Doing stuff')
        except Exception as e:
            self.fail(e)

    def test_start_custom_min_max(self):
        try:
            self.progress.start(min_value=100, max_value=300)
        except Exception as e:
            self.fail(e)

    def test_start_minimal_update(self):
        try:
            self.progress.start()
            self.progress.update(50)
        except Exception as e:
            self.fail(e)

    def test_start_minimal_update_raising(self):
        with self.assertRaises(Exception) as context:
            self.progress.start()
            self.progress.update(1000)

    def test_start_minimal_add(self):
        try:
            self.progress.start()
            self.progress.add(50)
        except Exception as e:
            self.fail(e)

    def test_start_minimal_add_raising(self):
        with self.assertRaises(Exception) as context:
            self.progress.start()
            self.progress.add(1000)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedTestCliProgress))
    return s
