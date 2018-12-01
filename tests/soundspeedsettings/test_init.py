import unittest
from hyo2.soundspeedsettings import app_info


class TestSoundSpeedSettingsInit(unittest.TestCase):

    def test_has_version(self):

        self.assertIsNot(len(app_info.app_version), 0)

    def test_is_version_more_than_3(self):
        self.assertGreaterEqual(int(app_info.app_version.split('.')[0]), 3)

    def test_has_doc(self):
        self.assertIsNot(len(app_info.app_name), 0)

    def test_is_sound_in_doc(self):
        self.assertTrue("sound" in app_info.app_name.lower())

    def test_has_author(self):
        self.assertIsNot(len(app_info.app_author), 0)

    def test_has_multiple_authors(self):
        self.assertGreater(len(app_info.app_author.split(';')), 0)

    def test_has_license(self):
        self.assertIsNot(len(app_info.app_license), 0)

    def test_has_lgpl_in_license(self):
        self.assertTrue("lgpl" in app_info.app_license.lower())

    def test_has_copyright(self):
        from hyo2.soundspeed import __copyright__
        self.assertIsNot(len(__copyright__), 0)

    def test_has_current_year_in_copyright(self):
        from hyo2.soundspeed import __copyright__
        from datetime import datetime
        self.assertTrue((("%s" % datetime.now().year) in __copyright__) or
                        (("%s" % (datetime.now().year + 1)) in __copyright__))


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedSettingsInit))
    return s
