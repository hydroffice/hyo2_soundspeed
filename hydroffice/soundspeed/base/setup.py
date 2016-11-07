from __future__ import absolute_import, division, print_function, unicode_literals

import logging

logger = logging.getLogger(__name__)

from .setup_db import SetupDb
from ..profile.dicts import Dicts
from ..client.clientlist import ClientList
from .helper import first_match


class Setup(object):

    def __init__(self, release_folder, use_setup_name=None):
        self.use_setup_name = use_setup_name

        self.setup_version = None
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

        # current settings
        self.current_project = None
        self.custom_projects_folder = None
        self.custom_outputs_folder = None
        self.custom_woa09_folder = None
        self.custom_woa13_folder = None
        self.noaa_tools = None
        self.default_survey = None
        self.default_vessel = None
        self.default_sn = None

        # loading settings
        self.release_folder = release_folder
        self.load_from_db()

    @property
    def db(self):
        """Usually the data_folder is set when the project is instantiated, so this is safe"""
        logger.debug("release_folder: %s, use setup: %s" % (self.release_folder, self.use_setup_name))
        return SetupDb(self.release_folder, use_setup_name=self.use_setup_name)

    def load_from_db(self):
        """Load/reload the setting from the setup db"""
        logger.info("*** > SETUP: loading ...")

        # try:

        db = self.db
        if db.setup_version > 1:
            raise RuntimeError("unsupported setup version: %s" % db.setup_version)

        self.setup_version = db.setup_version
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
            client_string = "%s:%s:%s:%s" % (client[1], client[2], client[3], client[4])
            self.client_list.add_client(client_string)
            logger.debug('- load: %s' % client_string)

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

        # current settings
        self.current_project = db.current_project
        self.custom_projects_folder = db.custom_projects_folder
        self.custom_outputs_folder = db.custom_outputs_folder
        self.custom_woa09_folder = db.custom_woa09_folder
        self.custom_woa13_folder = db.custom_woa13_folder
        self.noaa_tools = db.noaa_tools
        self.default_survey = db.default_survey
        self.default_vessel = db.default_vessel
        self.default_sn = db.default_sn

        db.close()

        # except Exception as e:
        #     raise RuntimeError("while loading db setup, %s" % e)

        logger.info("*** > SETUP: loaded!")

    def save_to_db(self):
        """Save setup to db"""
        logger.info("*** > SETUP: saving ...")

        try:
            db = self.db
            db.setup_version = self.setup_version
            # db.active_setup_id = self.setup_id  # obviously, unactivated to avoid db logic corruption
            # db.setup_status  # only the current setup is visualized
            # db.setup_name = self.setup_name

            # input
            db.use_woa09 = self.use_woa09
            db.use_woa13 = self.use_woa13
            db.use_rtofs = self.use_rtofs
            db.ssp_extension_source = first_match(Dicts.atlases, self.ssp_extension_source)
            db.ssp_salinity_source = first_match(Dicts.atlases, self.ssp_salinity_source)
            db.ssp_temp_sal_source = first_match(Dicts.atlases, self.ssp_temp_sal_source)
            db.ssp_up_or_down = first_match(Dicts.ssp_directions, self.ssp_up_or_down)

            db.rx_max_wait_time = self.rx_max_wait_time
            db.use_sis = self.use_sis
            db.use_sippican = self.use_sippican
            db.use_mvp = self.use_mvp

            # output
            db.append_caris_file = self.append_caris_file
            db.log_user = self.log_user
            db.log_server = self.log_server

            # client list
            db.delete_clients()
            for client in self.client_list.clients:
                logger.debug('- save: %s' % client.name)
                db.add_client(client_name=client.name,
                              client_ip=client.ip, client_port=client.port,
                              client_protocol=client.protocol)

            # listeners - sis
            db.sis_listen_port = self.sis_listen_port
            db.sis_listen_timeout = self.sis_listen_timeout
            db.sis_auto_apply_manual_casts = self.sis_auto_apply_manual_casts

            # listeners - sippican
            db.sippican_listen_port = self.sippican_listen_port
            db.sippican_listen_timeout = self.sippican_listen_timeout

            # listeners - mvp
            db.mvp_ip_address = self.mvp_ip_address
            db.mvp_listen_port = self.mvp_listen_port
            db.mvp_listen_timeout = self.mvp_listen_timeout
            db.mvp_transmission_protocol = self.mvp_transmission_protocol
            db.mvp_format = self.mvp_format
            db.mvp_winch_port = self.mvp_winch_port
            db.mvp_fish_port = self.mvp_fish_port
            db.mvp_nav_port = self.mvp_nav_port
            db.mvp_system_port = self.mvp_system_port
            db.mvp_sw_version = self.mvp_sw_version
            db.mvp_instrument_id = self.mvp_instrument_id
            db.mvp_instrument = self.mvp_instrument

            # server
            db.server_source = self.server_source
            db.server_apply_surface_sound_speed = self.server_apply_surface_sound_speed

            # current settings
            db.current_project = self.current_project
            db.custom_projects_folder = self.custom_projects_folder
            db.custom_outputs_folder = self.custom_outputs_folder
            db.custom_woa09_folder = self.custom_woa09_folder
            db.custom_woa13_folder = self.custom_woa13_folder
            db.noaa_tools = self.noaa_tools
            db.default_survey = self.default_survey
            db.default_vessel = self.default_vessel
            db.default_sn = self.default_sn

            db.close()

        except Exception as e:
            raise RuntimeError("while saving setup to db, %s" % e)

        logger.info("*** > SETUP: saved!")

    def __repr__(self):
        msg = "  <setup:%s:%s>\n" % (self.setup_id, self.setup_name)

        msg += "    <setup version: %d>\n" % self.setup_version

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
        msg += "    <current settings>\n"
        msg += "      <current_project: %s>\n" % self.current_project
        msg += "      <projects folder: %s>\n" % self.custom_projects_folder
        msg += "      <outputs folder: %s>\n" % self.custom_outputs_folder
        msg += "      <woa09 folder: %s>\n" % self.custom_woa09_folder
        msg += "      <woa13 folder: %s>\n" % self.custom_woa13_folder
        msg += "      <noaa tools: %s>\n" % self.noaa_tools
        msg += "      <default_survey: %s>\n" % self.default_survey
        msg += "      <default_vessel: %s>\n" % self.default_vessel
        msg += "      <default_sn: %s>\n" % self.default_sn

        return msg
