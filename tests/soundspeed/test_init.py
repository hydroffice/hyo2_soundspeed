import unittest

from hyo2.soundspeed import lib_info


class TestSoundSpeedInit(unittest.TestCase):

    def test_has_version(self):

        self.assertIsNot(len(lib_info.lib_version), 0)

    def test_is_version_more_than_3(self):
        self.assertGreaterEqual(int(lib_info.lib_version.split('.')[0]), 3)

    def test_has_doc(self):
        self.assertIsNot(len(lib_info.lib_name), 0)

    def test_is_sound_in_doc(self):
        self.assertTrue("sound" in lib_info.lib_name.lower())

    def test_has_author(self):
        self.assertIsNot(len(lib_info.lib_author), 0)

    def test_has_multiple_authors(self):
        self.assertGreater(len(lib_info.lib_author.split(';')), 0)

    def test_has_license(self):
        self.assertIsNot(len(lib_info.lib_license), 0)

    def test_has_lgpl_in_license(self):
        self.assertTrue("lgpl" in lib_info.lib_license.lower())

    def test_has_copyright(self):
        from hyo2.soundspeed import __copyright__
        self.assertIsNot(len(__copyright__), 0)

    def test_has_current_year_in_copyright(self):
        from hyo2.soundspeed import __copyright__
        from datetime import datetime
        self.assertTrue((("%s" % (datetime.now().year - 1)) in __copyright__) or
                        (("%s" % datetime.now().year) in __copyright__) or
                        (("%s" % (datetime.now().year + 1)) in __copyright__))


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedInit))
    return s
