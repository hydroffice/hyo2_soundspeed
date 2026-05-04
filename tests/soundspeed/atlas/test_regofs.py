import logging
import os
import shutil
import unittest

# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.atlas.regofs_model import RegOfsModel
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger()


class TestSoundSpeedAtlasRegofs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cur_dir = os.path.abspath(os.path.join(str(os.path.dirname(__file__)), "regofs"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.cur_dir)

    def test_is_present(self) -> None:
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        for model in RegOfsModel:
            self.assertFalse(model.lib_func_has_model(lib=prj)())
        prj.close()

    def test_download_model(self) -> None:
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        for model in RegOfsModel:
            if model in RegOfsModel.skip_models():
                continue
            self.assertTrue(model.lib_func_download_model(lib=prj)())
            self.assertTrue(model.lib_func_has_model(lib=prj)())
        prj.close()

    def test_query(self) -> None:
        prj = SoundSpeedLibrary(data_folder=self.cur_dir)
        for model in RegOfsModel:
            if model in RegOfsModel.skip_models():
                continue
            test = model.test
            self.assertIsNotNone(model.lib_func_query(lib=prj)(lat=test[0], lon=test[1], datestamp=test[2]))
        prj.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedAtlasRegofs))
    return s
