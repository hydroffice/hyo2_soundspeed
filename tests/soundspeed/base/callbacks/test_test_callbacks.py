import unittest
import os

from hyo.soundspeed.base.callbacks.test_callbacks import TestCallbacks


class TestSoundSpeedTestCallbacks(unittest.TestCase):

    def setUp(self):
        self.cb = TestCallbacks()

    def tearDown(self):
        pass

    def test_ask_number(self):
        self.assertTrue(isinstance(self.cb.ask_number(), float))

    def test_ask_text(self):
        self.assertTrue(type(self.cb.ask_text()) is str)

    def test_ask_date(self):
        from datetime import datetime as dt
        self.assertEqual(self.cb.ask_date().year, dt.utcnow().year)
        self.assertEqual(self.cb.ask_date().month, dt.utcnow().month)
        self.assertEqual(self.cb.ask_date().day, dt.utcnow().day)
        self.assertEqual(self.cb.ask_date().hour, dt.utcnow().hour)
        self.assertEqual(self.cb.ask_date().minute, dt.utcnow().minute)

        import sys
        if (sys.platform == 'win32') or (os.name is "nt"):
            self.assertEqual(self.cb.ask_date().second, dt.utcnow().second)

    def test_ask_location(self):
        loc = self.cb.ask_location()
        self.assertGreater(loc[0], 40.)
        self.assertGreater(loc[1], -80.)

    def test_ask_filename(self):
        self.assertTrue(os.path.exists(self.cb.ask_filename()))

    def test_ask_directory(self):
        self.assertTrue(os.path.exists(self.cb.ask_directory()))

    def test_ask_location_from_sis(self):
        self.assertTrue(self.cb.ask_location_from_sis())

    def test_ask_tss(self):
        self.assertTrue(type(self.cb.ask_tss()) is float)

    def test_ask_draft(self):
        self.assertTrue(type(self.cb.ask_draft()) is float)

    def test_msg_tx_no_verification(self):
        try:
            self.cb.msg_tx_no_verification("", "")
        except Exception as e:
            self.fail(e)

    def test_msg_tx_sis_wait(self):
        try:
            self.cb.msg_tx_sis_wait("")
        except Exception as e:
            self.fail(e)

    def test_msg_tx_sis_confirmed(self):
        try:
            self.cb.msg_tx_sis_confirmed("")
        except Exception as e:
            self.fail(e)

    def test_msg_tx_sis_not_confirmed(self):
        try:
            self.cb.msg_tx_sis_not_confirmed("", 0)
        except Exception as e:
            self.fail(e)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedTestCallbacks))
    return s
