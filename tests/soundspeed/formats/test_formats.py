import unittest
import os
import logging

from hyo2.soundspeedmanager import AppInfo
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary
from hyo2.soundspeed.base.callbacks.test_callbacks import TestCallbacks
from hyo2.soundspeed.base.testing import SoundSpeedTesting

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

reduced_testing = True


class TestSoundSpeedFormats(unittest.TestCase):

    def setUp(self):
        self.output_formats = ["asvp", "caris", "csv", "elac", "hypack", "ixblue", "qps", "sonardyne", "unb", ]
        data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
        self.testing = SoundSpeedTesting(root_folder=data_folder)
        self.data_output = self.testing.output_data_folder()

    def tearDown(self):
        pass

    def test_read_store_and_write_aml(self):
        filters = ["aml", ]
        self._run(filters=filters)

    def test_read_store_and_write_aoml(self):
        filters = ["aoml", ]
        self._run(filters=filters)

    def test_read_store_and_write_asvp(self):
        filters = ["asvp", ]
        self._run(filters=filters)

    def test_read_store_and_write_caris(self):
        filters = ["caris", ]
        self._run(filters=filters)

    def test_read_store_and_write_castaway(self):
        filters = ["castaway", ]
        self._run(filters=filters)

    def test_read_store_and_write_digibarpro(self):
        filters = ["digibarpro", ]
        self._run(filters=filters)

    def test_read_store_and_write_digibars(self):
        filters = ["digibars", ]
        self._run(filters=filters)

    def test_read_store_and_write_elac(self):
        filters = ["elac", ]
        self._run(filters=filters)

    def test_read_store_and_write_idronaut(self):
        filters = ["idronaut", ]
        self._run(filters=filters)

    def test_read_store_and_write_iss(self):
        filters = ["iss", ]
        self._run(filters=filters)

    def test_read_store_and_write_mvp(self):
        filters = ["mvp", ]
        self._run(filters=filters)

    def test_read_store_and_write_oceanscience(self):
        filters = ["oceanscience", ]
        self._run(filters=filters)

    def test_read_store_and_write_saiv(self):
        filters = ["saiv", ]
        self._run(filters=filters)

    def test_read_store_and_write_seaandsun(self):
        filters = ["seaandsun", ]
        self._run(filters=filters)

    def test_read_store_and_write_seabird(self):
        filters = ["seabird", ]
        self._run(filters=filters)

    def test_read_store_and_write_sippican(self):
        filters = ["sippican", ]
        self._run(filters=filters)

    def test_read_store_and_write_sonardyne(self):
        filters = ["sonardyne", ]
        self._run(filters=filters)

    # TODO: commented out since it fails only on CI after having timed out
    # def test_read_store_and_write_turo(self):
    #     filters = ["turo", ]
    #     self._run(filters=filters)

    def test_read_store_and_write_unb(self):
        filters = ["unb", ]
        self._run(filters=filters)

    def test_read_store_and_write_valeport(self):
        filters = ["valeport", ]
        self._run(filters=filters)

    def _run(self, filters):
        # create a project with test-callbacks
        lib = SoundSpeedLibrary(callbacks=TestCallbacks())

        # set the current project name
        lib.setup.current_project = 'test_read_store_and_write'

        tests = self.testing.input_dict_test_files(inclusive_filters=filters)
        data_outputs = dict()
        for format in self.output_formats:
            data_outputs[format] = self.data_output

        for idx, testfile in enumerate(tests.keys()):

            if reduced_testing and (os.path.basename(testfile)[0] != "_"):
                continue
            logger.info("test: * New profile: #%03d * -> %s" % (idx, os.path.basename(testfile)))

            lib.import_data(data_path=testfile, data_format=tests[testfile].name)

            lib.store_data()

            lib.export_data(data_paths=data_outputs, data_formats=self.output_formats)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedFormats))
    return s
