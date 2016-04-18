from __future__ import absolute_import, division, print_function, unicode_literals


import logging

logger = logging.getLogger(__name__)

from .settingsdb import SettingsDb
from ..profile.dicts import Dicts
from ..client.clientlist import ClientList


class Settings(object):

    def __init__(self, data_folder):
        self.library_version = None
        self.setup_id = None
        self.setup_name = None

        # input
        self.use_woa09 = None
        self.use_woa13 = None
        self.use_rtofs = None
        self.ssp_extension_source = None
        self.ssp_salinity_source = None
        self.ssp_temp_sal_source = None
        self.ssp_up_or_down = None
        self.rx_max_wait_time = None
        self.use_sis = None
        self.use_sippican = None
        self.use_mvp = None

        # output
        self.append_caris_file = None
        self.log_user = None
        self.log_server = None
        self.client_list = ClientList()

        # listeners - sis
        self.sis_listen_port = None
        self.sis_listen_timeout = None
        self.sis_auto_apply_manual_casts = None
        # listeners - sippican
        self.sippican_listen_port = None
        self.sippican_listen_timeout = None
        # listeners - mvp
        self.mvp_ip_address = None
        self.mvp_listen_port = None
        self.mvp_listen_timeout = None
        self.mvp_transmission_protocol = None
        self.mvp_format = None
        self.mvp_winch_port = None
        self.mvp_fish_port = None
        self.mvp_nav_port = None
        self.mvp_system_port = None
        self.mvp_sw_version = None
        self.mvp_instrument_id = None
        self.mvp_instrument = None

        # server
        self.server_source = None
        self.server_append_caris_file = None
        self.server_apply_surface_sound_speed = None
        self.server_auto_export_on_send = None

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

        # input
        self.use_woa09 = db.use_woa09
        self.use_woa13 = db.use_woa13
        self.use_rtofs = db.use_rtofs
        self.ssp_extension_source = Dicts.atlases[db.ssp_extension_source]
        self.ssp_salinity_source = Dicts.atlases[db.ssp_salinity_source]
        self.ssp_temp_sal_source = Dicts.atlases[db.ssp_temp_sal_source]
        self.ssp_up_or_down = Dicts.ssp_directions[db.ssp_up_or_down]
        self.rx_max_wait_time = db.rx_max_wait_time
        self.use_sis = db.use_sis
        self.use_sippican = db.use_sippican
        self.use_mvp = db.use_mvp

        # output
        self.append_caris_file = db.append_caris_file
        self.log_user = db.log_user
        self.log_server = db.log_server
        # client list
        self.client_list = ClientList()  # to reset the list
        for client in db.client_list:
            client_string = "\"%s\":%s:%s:%s" % (client[1], client[2], client[3], client[4])
            self.client_list.add_client(client_string)

        # listeners - sis
        self.sis_listen_port = db.sis_listen_port
        self.sis_listen_timeout = db.sis_listen_timeout
        self.sis_auto_apply_manual_casts = db.sis_auto_apply_manual_casts

        # listeners - sippican
        self.sippican_listen_port = db.sippican_listen_port
        self.sippican_listen_timeout = db.sippican_listen_timeout

        # listeners - mvp
        self.mvp_ip_address = db.mvp_ip_address
        self.mvp_listen_port = db.mvp_listen_port
        self.mvp_listen_timeout = db.mvp_listen_timeout
        self.mvp_transmission_protocol = db.mvp_transmission_protocol
        self.mvp_format = db.mvp_format
        self.mvp_winch_port = db.mvp_winch_port
        self.mvp_fish_port = db.mvp_fish_port
        self.mvp_nav_port = db.mvp_nav_port
        self.mvp_system_port = db.mvp_system_port
        self.mvp_sw_version = db.mvp_sw_version
        self.mvp_instrument_id = db.mvp_instrument_id
        self.mvp_instrument = db.mvp_instrument

        # server
        self.server_source = db.server_source
        self.server_apply_surface_sound_speed = db.server_apply_surface_sound_speed
        db.close()

    def __repr__(self):
        msg = "  <setup:%s:%s>\n" % (self.setup_id, self.setup_name)
        msg += "    <library version: %s>" % self.library_version
        msg += "    <input>\n"
        msg += "      <use_woa09: %s>\n" % self.use_woa09
        msg += "      <use_woa13: %s>\n" % self.use_woa13
        msg += "      <use_rtofs: %s>\n" % self.use_rtofs
        msg += "      <ssp_extension_source: %s>\n" % self.ssp_extension_source
        msg += "      <ssp_salinity_source: %s>\n" % self.ssp_salinity_source
        msg += "      <ssp_temp_sal_source: %s>\n" % self.ssp_temp_sal_source
        msg += "      <up_or_down: %s>\n" % self.ssp_up_or_down
        msg += "      <rx_max_wait_time: %s>\n" % self.rx_max_wait_time
        msg += "      <use_sis: %s>\n" % self.use_sis
        msg += "      <use_sippican: %s>\n" % self.use_sippican
        msg += "      <use_mvp: %s>\n" % self.use_mvp
        msg += "    <output>\n"
        msg += "      <append_caris_file: %s>\n" % self.append_caris_file
        msg += "      <log_user: %s>\n" % self.log_user
        msg += "      <log_server: %s>\n" % self.log_server
        msg += "      <clients>\n"
        for c in self.client_list.clients:
            msg += "        <%s>\n" % c
        msg += "    <listeners - sis>\n"
        msg += "      <sis_listen_port: %s>\n" % self.sis_listen_port
        msg += "      <sis_listen_timeout: %s>\n" % self.sis_listen_timeout
        msg += "      <sis_auto_apply_manual_casts: %s>\n" % self.sis_auto_apply_manual_casts
        msg += "    <listeners - sippican>\n"
        msg += "      <sippican_listen_port: %s>\n" % self.sippican_listen_port
        msg += "      <sippican_listen_timeout: %s>\n" % self.sippican_listen_timeout
        msg += "    <listeners - mvp>\n"
        msg += "      <mvp_ip_address: %s>\n" % self.mvp_ip_address
        msg += "      <mvp_listen_port: %s>\n" % self.mvp_listen_port
        msg += "    <server>\n"
        msg += "      <server_source: %s>\n" % self.server_source
        msg += "      <server_append_caris_file: %s>\n" % self.server_append_caris_file
        msg += "      <server_apply_surface_sound_speed: %s>\n" % self.server_apply_surface_sound_speed
        msg += "      <server_auto_export_on_send: %s>\n" % self.server_auto_export_on_send

        return msg
