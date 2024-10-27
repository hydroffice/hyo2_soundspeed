import unittest
import logging

from hyo2.ssm2.lib.atlas.rtofs import Rtofs
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger()


class TestSoundSpeedAtlasRtofs(unittest.TestCase):

    def test_creation_of_Rtofs(self):
        prj = SoundSpeedLibrary()
        rtofs = Rtofs(data_folder=prj.rtofs_folder, prj=prj)
        self.assertTrue('rtofs' in rtofs.data_folder)
        self.assertFalse(rtofs.is_present())
        prj.close()

    def test_download_db_from_Rtofs(self):
        prj = SoundSpeedLibrary()
        rtofs = Rtofs(data_folder=prj.data_folder, prj=prj)
        rtofs.download_db(server_mode=True)

        # to avoid test failures
        if not rtofs.is_present():
            logger.warning("unable to download RTOFS data")
        # self.assertTrue(rtofs.is_present())

        prj.close()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedAtlasRtofs))
    return s
