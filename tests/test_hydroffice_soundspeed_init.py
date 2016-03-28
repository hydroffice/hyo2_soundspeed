from __future__ import absolute_import, division, print_function, unicode_literals

import unittest


class TestSoundSpeedInit(unittest.TestCase):

    def test_version(self):
        """Test that there is a version string"""
        from hydroffice.soundspeed import __version__
        version = __version__
        str_len = len(version)
        self.assertIsNot(str_len, 0)

    def test_doc(self):
        """Test that there is a doc string"""
        from hydroffice.soundspeed import __doc__
        doc = __doc__
        str_len = len(doc)
        self.assertIsNot(str_len, 0)

    def test_author(self):
        """Test that there is an author string"""
        from hydroffice.soundspeed import __author__
        author = __author__
        str_len = len(author)
        self.assertIsNot(str_len, 0)

    def test_license(self):
        """Test that there is a license string"""
        from hydroffice.soundspeed import __license__
        license = __license__
        str_len = len(license)
        self.assertIsNot(str_len, 0)

    def test_copyright(self):
        """Test that there is a copyright string"""
        from hydroffice.soundspeed import __copyright__
        license = __copyright__
        str_len = len(license)
        self.assertIsNot(str_len, 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedInit))
    return s
