import unittest
import os

from hyo.soundspeed.atlas.ftp import Ftp
from hyo.soundspeed.base import testing


class TestFtp(unittest.TestCase):

    def test_init(self):
        ftp = Ftp(host="ftp.ccom.unh.edu", password="test@gmail.com", show_progress=True, debug_mode=True)
        ftp.disconnect()

    def test_get_file(self):
        ftp = Ftp(host="ftp.ccom.unh.edu", password="test@gmail.com", show_progress=True, debug_mode=True)
        ftp.get_file(file_src="fromccom/hydroffice/Caris_Support_Files_5_5.zip",
                     file_dst=os.path.join(testing.output_data_folder(), "test.zip"))
        ftp.disconnect()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFtp))
    return s
