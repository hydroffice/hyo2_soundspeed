import unittest

from hyo2.ssm2 import pkg_info


class TestSoundSpeedInit(unittest.TestCase):

    def test_has_version(self):

        self.assertIsNot(len(pkg_info.version), 0)

    def test_is_version_more_than_3(self):
        self.assertGreaterEqual(int(pkg_info.version.split('.')[0]), 3)

    def test_has_doc(self):
        self.assertIsNot(len(pkg_info.name), 0)

    def test_is_sound_in_doc(self):
        self.assertTrue("sound" in pkg_info.name.lower())

    def test_has_author(self):
        self.assertIsNot(len(pkg_info.author), 0)

    def test_has_multiple_authors(self):
        self.assertGreater(len(pkg_info.author.split(';')), 0)

    def test_has_license(self):
        self.assertIsNot(len(pkg_info.lic), 0)

    def test_has_lgpl_in_license(self):
        self.assertTrue("lgpl" in pkg_info.lic.lower())

    def test_has_copyright(self):
        from hyo2.ssm2 import __copyright__
        self.assertIsNot(len(__copyright__), 0)

    def test_has_current_year_in_copyright(self):
        from hyo2.ssm2 import __copyright__
        from datetime import datetime
        self.assertTrue((("%s" % (datetime.now().year - 1)) in __copyright__) or
                        (("%s" % datetime.now().year) in __copyright__) or
                        (("%s" % (datetime.now().year + 1)) in __copyright__))


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedInit))
    return s
