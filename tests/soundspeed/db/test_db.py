import os
import unittest
from datetime import datetime
import numpy as np

from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary
from hyo2.ssm2.lib.profile.profilelist import ProfileList


class TestSoundSpeedDb(unittest.TestCase):
    def setUp(self):
        def add_cast(lat, lon):
            self.lib.ssp.cur.meta.latitude = lat
            self.lib.ssp.cur.meta.longitude = lon
            self.lib.ssp.cur.meta.utc_time = datetime.now()
            self.lib.ssp.cur.init_data(self.levels)
            self.lib.ssp.cur.data.depth[:self.levels] = self.depth
            self.lib.ssp.cur.data.speed[:self.levels] = 1415
            self.lib.restart_proc()
            self.lib.store_data()

        self.max_pk = 5
        self.levels = self.max_pk * self.max_pk
        self.depth = np.array(range(self.levels))
        projects_folder = os.path.abspath(os.curdir)
        project_name = 'unittest'
        db_name = '%s.db' % project_name
        self.db_path = os.path.join(projects_folder, db_name)
        self.tearDown()
        self.lib = SoundSpeedLibrary()
        self.lib.projects_folder = projects_folder
        self.lib.current_project = project_name
        self.lib.ssp = ProfileList()
        self.lib.ssp.append()
        if len(self.lib.db_list_profiles()) < self.max_pk:
            for i in range(self.max_pk):
                add_cast(20 + i, -75)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # @unittest.skipUnless(sys.platform.startswith("win"), "only works with GDAL < 2.0 on Windows")
    def test_save_load_cast(self):
        def test_pk(pkey):
            self.lib.ssp = self.lib.db_retrieve_profile(pkey)
            self.lib.store_data()
            self.lib.ssp = self.lib.db_retrieve_profile(pkey)
            sum_ = len(self.lib.ssp.cur.proc.speed) + len(self.lib.ssp.cur.proc.depth)
            sum_ += len(self.lib.ssp.cur.data.speed) + len(self.lib.ssp.cur.data.depth)
            self.assertEqual(sum_, self.levels * 4)
            self.assertTrue((self.lib.ssp.cur.data.depth == self.depth).all())
            self.assertTrue((self.lib.ssp.cur.proc.depth == self.depth).all())

        for i in range(self.levels):
            # pk = random.randint(1, self.max_pk)
            pk = i % self.max_pk + 1
            test_pk(pk)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedDb))
    return s
