from __future__ import absolute_import, division, print_function, unicode_literals

import unittest


class TestSoundSpeedManagerInit(unittest.TestCase):

    def test_has_version(self):
        from hydroffice.soundspeedmanager import __version__
        self.assertIsNot(len(__version__), 0)

    def test_is_version_more_than_3(self):
        from hydroffice.soundspeedmanager import __version__
        self.assertGreaterEqual(int(__version__.split('.')[0]), 3)

    def test_doc(self):
        from hydroffice.soundspeedmanager import __doc__
        self.assertIsNot(len(__doc__), 0)

    def test_is_sound_in_doc(self):
        from hydroffice.soundspeedmanager import __doc__
        self.assertTrue("sound" in __doc__.lower(), 0)

    def test_author(self):
        from hydroffice.soundspeedmanager import __author__
        self.assertIsNot(len(__author__), 0)

    def test_has_multiple_authors(self):
        from hydroffice.soundspeedmanager import __author__
        self.assertGreater(len(__author__.split(';')), 0)

    def test_license(self):
        from hydroffice.soundspeedmanager import __license__
        self.assertIsNot(len(__license__), 0)

    def test_has_lgpl_in_license(self):
        from hydroffice.soundspeedmanager import __license__
        self.assertTrue("lgpl" in __license__.lower())

    def test_copyright(self):
        from hydroffice.soundspeedmanager import __copyright__
        self.assertIsNot(len(__copyright__), 0)

    def test_has_current_year_in_copyright(self):
        from hydroffice.soundspeedmanager import __copyright__
        from datetime import datetime
        self.assertTrue((("%s" % datetime.now().year) in __copyright__) or
                        (("%s" % (datetime.now().year + 1)) in __copyright__))


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedManagerInit))
    return s
