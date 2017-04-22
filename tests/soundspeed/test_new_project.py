import unittest


class TestSoundSpeedNewProject(unittest.TestCase):

    def test_available_projects(self):
        from hyo.soundspeed.soundspeed import SoundSpeedLibrary

        lib = SoundSpeedLibrary()
        ssp_list = lib.db_list_profiles()
        self.assertGreaterEqual(len(ssp_list), 0)

        prj_list = lib.list_projects()
        self.assertGreaterEqual(len(prj_list), 1)

        lib.close()

    def test_new_projects(self):
        from hyo.soundspeed.soundspeed import SoundSpeedLibrary

        lib = SoundSpeedLibrary()
        ssp_list = lib.db_list_profiles()
        self.assertGreaterEqual(len(ssp_list), 0)

        lib.current_project = "zzz"
        ssp_list = lib.db_list_profiles()
        self.assertGreaterEqual(len(ssp_list), 0)

        prj_list = lib.list_projects()
        self.assertGreaterEqual(len(prj_list), 2)

        lib.current_project = "aaa"
        lib.remove_project("zzz")
        prj_list = lib.list_projects()
        self.assertGreaterEqual(len(prj_list), 1)

        lib.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedNewProject))
    return s
