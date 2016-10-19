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

from hydroffice.soundspeed.logging import sqlitelogging


class TestSoundSpeedLoggingSqliteLogging(unittest.TestCase):

    def setUp(self):
        self.output_folder = os.path.abspath(os.path.dirname(__file__))
        self.server_db = 'server.db'
        self.user_db = 'user.db'

    def tearDown(self):
        if os.path.exists(os.path.join(self.output_folder, self.server_db)):
            os.remove(os.path.join(self.output_folder, self.server_db))
        if os.path.exists(os.path.join(self.output_folder, self.user_db)):
            os.remove(os.path.join(self.output_folder, self.user_db))

    def test_creation_of_SqliteLogging(self):
        logs = sqlitelogging.SqliteLogging(output_folder=self.output_folder, server_db_file=self.server_db,
                                           user_db_file=self.user_db)
        self.assertTrue(os.path.exists(os.path.join(self.output_folder, self.server_db)))
        self.assertTrue(os.path.exists(os.path.join(self.output_folder, self.user_db)))
        self.assertFalse(logs.user_active)
        self.assertFalse(logs.server_active)

    def test_activate_user_db_for_SqliteLogging(self):
        logs = sqlitelogging.SqliteLogging(output_folder=self.output_folder, server_db_file=self.server_db,
                                           user_db_file=self.user_db)
        logs.activate_user_db()
        self.assertTrue(logs.user_active)
        logs.deactivate_user_db()
        self.assertFalse(logs.user_active)

    def test_activate_server_db_for_SqliteLogging(self):
        logs = sqlitelogging.SqliteLogging(output_folder=self.output_folder, server_db_file=self.server_db,
                                           user_db_file=self.user_db)
        logs.activate_server_db()
        self.assertTrue(logs.server_active)
        logs.deactivate_server_db()
        self.assertFalse(logs.server_active)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedLoggingSqliteLogging))
    return s
