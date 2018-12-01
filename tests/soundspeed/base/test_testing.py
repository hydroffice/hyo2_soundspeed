import unittest
import os

from hyo2.soundspeed.base.testing import SoundSpeedTesting


class TestSoundSpeedTesting(unittest.TestCase):

    def setUp(self):
        self.testing = SoundSpeedTesting(
            root_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)))

    def tearDown(self):
        pass

    def test_root_data_folder(self):
        self.assertTrue(os.path.exists(self.testing.root_data_folder()))

    def test_input_data_folder(self):
        self.assertTrue(os.path.exists(self.testing.input_data_folder()))

    def test_input_data_sub_folders(self):
        self.assertGreater(len(self.testing.input_data_sub_folders()), 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedTesting))
    return s
