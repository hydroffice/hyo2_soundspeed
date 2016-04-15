from __future__ import absolute_import, division, print_function, unicode_literals


import logging

logger = logging.getLogger(__name__)

from .settingsdb import SettingsDb
from ..profile.dicts import Dicts
from .clientlist import ClientList


class Settings(object):

    def __init__(self, data_folder):
        self.library_version = None
        self.setup_id = None
        self.setup_name = None

        # processing
        self.ssp_up_or_down = None

        # atlases
        self.use_woa09 = None
        self.use_woa13 = None
        self.use_rtofs = None

        # logging
        self.log_user = None
        self.log_server = None

        # client list
        self.client_list = ClientList()

        # loading settings
        self.data_folder = data_folder
        self.load_settings_from_db()

    @property
    def db(self):
        return SettingsDb(self.data_folder)

    def load_settings_from_db(self):
        db = self.db
        self.library_version = db.library_version
        self.setup_id = db.active_setup_id
        self.setup_name = db.setup_name
        self.ssp_up_or_down = Dicts.ssp_directions[db.ssp_up_or_down]
        # atlases
        self.use_woa09 = db.use_woa09
        self.use_woa13 = db.use_woa13
        self.use_rtofs = db.use_rtofs
        # logging
        self.log_user = db.log_user
        self.log_server = db.log_server
        # client list
        self.client_list = ClientList()  # to reset the list
        for client in db.client_list:
            client_string = "\"%s\":%s:%s:%s" % (client[1], client[2], client[3], client[4])
            self.client_list.add_client(client_string)
        db.close()

    def __repr__(self):
        msg = "  <setup:%s:%s>\n" % (self.setup_id, self.setup_name)
        msg += "    <library version: %s>" % self.library_version
        msg += "    <ssp>\n"
        msg += "      <up_or_down: %s>\n" % self.ssp_up_or_down
        msg += "    <atlases>\n"
        msg += "      <use_woa09: %s>\n" % self.use_woa09
        msg += "      <use_woa13: %s>\n" % self.use_woa13
        msg += "      <use_rtofs: %s>\n" % self.use_rtofs
        msg += "    <logging>\n"
        msg += "      <log_user: %s>\n" % self.log_user
        msg += "      <log_server: %s>\n" % self.log_server
        msg += "    <clients>\n"
        for c in self.client_list:
            msg += "      <%s>\n" % c
        return msg
