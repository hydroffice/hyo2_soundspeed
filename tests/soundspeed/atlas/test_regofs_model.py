import unittest
import os
import shutil
import logging
from collections.abc import Callable
from datetime import datetime, timezone, timedelta

from hyo2.ssm2.lib.atlas.regofs import RegOfsModel
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger()


class TestSoundSpeedAtlasRegofsModel(unittest.TestCase):

    def setUp(self):
        self.cur_dir = os.path.abspath(os.path.dirname(__file__))

    def tearDown(self):
        dir_items = os.listdir(self.cur_dir)
        for item in dir_items:
            if item.split('.')[-1] == 'db':
                os.remove(os.path.join(self.cur_dir, item))
            if item == 'atlases':
                shutil.rmtree(os.path.join(self.cur_dir, item))

    def test_model_enum(self) -> None:
        for model in RegOfsModel:
            self.assertIsInstance(model.name, str)
            self.assertIsInstance(model.value, int)
            self.assertIsInstance(model.description, str)
            self.assertIsInstance(model.slug, str)
            self.assertIsInstance(model.cycle_hour, str)

    def test_test(self) -> None:
        for model in RegOfsModel:
            test_tuple = model.test
            self.assertEqual(len(test_tuple), 3)
            lat = test_tuple[0]
            self.assertIsInstance(lat, float)
            self.assertTrue(-90.0 <= lat <= 90.0)
            lon = test_tuple[1]
            self.assertIsInstance(lon, float)
            self.assertTrue(-180.0 <= lon <= 180.0)
            ts = test_tuple[2]
            min_ts = datetime.now(tz=timezone.utc) - timedelta(hours=1)
            max_ts = datetime.now(tz=timezone.utc) + timedelta(hours=1)
            self.assertIsInstance(ts, datetime)
            self.assertTrue(min_ts <= ts <= max_ts)

    def test_valid_download_url(self) -> None:
        for model in RegOfsModel:
            if model in RegOfsModel.skip_models():
                continue
            url = model.valid_download_url()
            self.assertIsNotNone(url, model.name)

    def test_valid_opendap_url(self) -> None:
        for model in RegOfsModel:
            if model in RegOfsModel.skip_models():
                continue
            url = model.valid_opendap_url()
            self.assertIsNotNone(url, model.name)

    def test_lib_func(self) -> None:
        lib = SoundSpeedLibrary()
        for model in RegOfsModel:
            self.assertIsInstance(model.lib_func_has_model(lib=lib), Callable, model.name)
            self.assertIsInstance(model.lib_func_download_model(lib=lib), Callable, model.name)
            self.assertIsInstance(model.lib_func_query(lib=lib), Callable, model.name)

def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedAtlasRegofsModel))
    return s
