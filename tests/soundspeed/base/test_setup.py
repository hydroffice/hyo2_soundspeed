import unittest
import os

from hyo2.soundspeed.base.setup import Setup


class TestSoundSpeedSetup(unittest.TestCase):

    def setUp(self):
        self.data_folder = os.path.abspath(os.curdir)
        self.db_name = "setup.db"
        self.db_path = os.path.join(self.data_folder, self.db_name)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_create_settings_and_check_db_path(self):
        settings = Setup(self.data_folder)
        db = settings.db
        self.assertEqual(db.db_path, self.db_path)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedSetup))
    return s
