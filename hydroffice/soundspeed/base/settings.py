from __future__ import absolute_import, division, print_function, unicode_literals


import logging

logger = logging.getLogger(__name__)

from .settingsdb import SettingsDb


class Settings(object):

    def __init__(self, data_folder):
        self.library_version = None
        self.setup_id = None
        self.setup_name = None

        # loading settings
        self.data_folder = data_folder
        self.load_settings_from_db()

    def load_settings_from_db(self):
        db = SettingsDb(self.data_folder)
        self.library_version = db.library_version
        self.setup_id = db.active_setup_id
        self.setup_name = db.setup_name

    def __repr__(self):
        msg = "  <setup:%s:%s>\n" % (self.setup_id, self.setup_name)
        msg += "    <library version: %s>" % self.library_version
        return msg
