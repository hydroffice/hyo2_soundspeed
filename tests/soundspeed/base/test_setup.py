import unittest
import os

from hyo2.ssm2.lib.base.setup import Setup


class TestSoundSpeedSetup(unittest.TestCase):

    def setUp(self):
        self.data_folder = os.path.abspath(os.path.dirname(__file__))
        self.db_name = "setup.db"
        self.db_path = os.path.join(self.data_folder, self.db_name)

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                return

    def test_create_settings_and_check_db_path(self):
        settings = Setup(release_folder=self.data_folder)
        db = settings.db
        self.assertEqual(db.db_path, self.db_path)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedSetup))
    return s
