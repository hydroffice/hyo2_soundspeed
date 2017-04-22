from datetime import datetime
import os
import random
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.base.callbacks.abstract_callbacks import AbstractCallbacks


class TestCallbacks(AbstractCallbacks):
    """Used only for testing since the methods do not require user interaction"""

    def ask_number(self, title="", msg="Enter number", default=0.0,
                   min_value=-2147483647.0, max_value=2147483647.0, decimals=7):
        return random.random() * 100.0

    def ask_text(self, title="", msg="Enter text"):
        return "Hello world"

    def ask_date(self):
        return datetime.utcnow()

    def ask_location(self):
        return 43.13555 + random.random(), -70.9395 + random.random()

    def ask_filename(self, saving=True, key_name=None, default_path=".",
                     title="Choose a path/filename", default_file="",
                     file_filter="All Files|*.*", multi_file=False):
        return os.path.normpath(__file__)

    def ask_directory(self, key_name=None, default_path=".",
                      title="Browse for folder", message=""):
        return os.path.normpath(os.path.dirname(__file__))

    def ask_location_from_sis(self):
        return True

    def ask_tss(self):
        return 1500.0

    def ask_draft(self):
        return 8.0

    def msg_tx_no_verification(self, name, protocol):
        """Profile transmitted but not verification available"""
        pass

    def msg_tx_sis_wait(self, name):
        """Profile transmitted, SIS is waiting for confirmation"""
        pass

    def msg_tx_sis_confirmed(self, name):
        """Profile transmitted, SIS confirmed"""
        pass

    def msg_tx_sis_not_confirmed(self, name, ip):
        """Profile transmitted, SIS not confirmed"""
        pass
