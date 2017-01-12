from __future__ import absolute_import, division, print_function, unicode_literals

import unittest


class TestSoundSpeedNewProject(unittest.TestCase):

    def test_available_projects(self):
        from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary

        lib = SoundSpeedLibrary()
        prj_list = lib.list_projects()

        self.assertGreaterEqual(len(prj_list), 1)

        lib.close()

    def test_new_projects(self):
        from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary

        lib = SoundSpeedLibrary()
        lib.setup.current_project = "test"
        prj_list = lib.list_projects()

        self.assertGreaterEqual(len(prj_list), 2)

        lib.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedNewProject))
    return s
