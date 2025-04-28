import logging
import os

from hyo2.abc2.lib.package.pkg_helper import PkgHelper
from hyo2.ssm2.lib.base.setup_db import SetupDb
from hyo2.ssm2.lib.base.setup_sql import setup_version
from hyo2.ssm2.lib.profile.dicts import Dicts
from hyo2.ssm2.lib.client.clientlist import ClientList

logger = logging.getLogger(__name__)


class Setup:

    SUPPORTED_VERSION = setup_version

    @classmethod
    def are_updates_required(cls, db_path: str) -> bool:
        # logger.debug("check if version updates are required for %s" % db_path)
        db = SetupDb(os.path.dirname(db_path))
        # logger.debug(db.setup_version)
        if db.setup_version < cls.SUPPORTED_VERSION:
            return True
        return False

    @classmethod
    def apply_required_updates(cls, db_path: str) -> bool:
        logger.debug("applying version updates %s" % db_path)
        db = SetupDb(os.path.dirname(db_path))
        if db.setup_version < cls.SUPPORTED_VERSION:
            success = db.update_from_v1_to_v7()
            if success:
                return True
        return False

    def __init__(self, release_folder: str, use_setup_name: str | None = None):
        self.use_setup_name = use_setup_name

        self.setup_version: int | None = None
        self.setup_id: int | None = None
        self.setup_name: str | None = None

        # input
        self.use_woa09: bool | None = None
        self.use_woa13: bool | None = None
        self.use_woa18: bool | None = None
        self.use_woa23: bool | None = None
        self.use_rtofs: bool | None = None
        self.use_cbofs: bool | None = None
        self.use_dbofs: bool | None = None
        self.use_gomofs: bool | None = None
        self.use_nyofs: bool | None = None
        self.use_sjrofs: bool | None = None
        self.use_ngofs2: bool | None = None
        self.use_tbofs: bool | None = None
        self.use_leofs: bool | None = None
        self.use_lmhofs: bool | None = None
        self.use_loofs: bool | None = None
        self.use_lsofs: bool | None = None
        self.use_sscofs: bool | None = None
        self.use_sfbofs: bool | None = None
        self.ssp_extension_source: str | None = None
        self.ssp_salinity_source: str | None = None
        self.ssp_temp_sal_source: str | None = None
        self.ssp_up_or_down: str | None = None
        self.rx_max_wait_time: int | None = None
        self.use_sis4: bool | None = None
        self.use_sis5: bool | None = None
        self.use_sippican: bool | None = None
        self.use_nmea_0183: bool | None = None
        self.use_mvp: bool | None = None

        # output
        self.client_list = ClientList()

        # listeners - sis
        self.sis_listen_port: int | None = None
        self.sis_listen_timeout: int | None = None
        # output - sis 4 and 5
        self.sis_auto_apply_manual_casts: bool | None = None
        # listeners - sippican
        self.sippican_listen_port: int | None = None
        self.sippican_listen_timeout: int | None = None
        # listeners - nmea
        self.nmea_listen_port: int | None = None
        self.nmea_listen_timeout: int | None = None
        # listeners - mvp
        self.mvp_ip_address: str | None = None
        self.mvp_listen_port: int | None = None
        self.mvp_listen_timeout: int | None = None
        self.mvp_transmission_protocol = None
        self.mvp_format: str | None = None
        self.mvp_winch_port: int | None = None
        self.mvp_fish_port: int | None = None
        self.mvp_nav_port: int | None = None
        self.mvp_system_port: int | None = None
        self.mvp_sw_version: str | None = None
        self.mvp_instrument_id: str | None = None
        self.mvp_instrument: str | None = None

        # server
        self.server_source: str | None = None
        self.server_apply_surface_sound_speed: bool | None = None
        self.server_max_failed_attempts: int | None = None

        # current settings
        self.current_project: str | None = None
        self.custom_projects_folder: str | None = None
        self.custom_outputs_folder: str | None = None
        self.custom_woa09_folder: str | None = None
        self.custom_woa13_folder: str | None = None
        self.custom_woa18_folder: str | None = None
        self.custom_woa23_folder: str | None = None
        self.noaa_tools: bool | None = None
        self.default_institution: str | None = None
        self.default_survey: str | None = None
        self.default_vessel: str | None = None
        self.average_sound_speed: bool | None = None
        self.auto_apply_default_metadata: bool | None = None

        # loading settings
        self.release_folder: str | None = release_folder
        self.load_from_db()

    @property
    def use_sis(self) -> bool:
        return self.use_sis4 or self.use_sis5

    @property
    def db(self) -> SetupDb:
        """Usually the data_folder is set when the project is instantiated, so this is safe"""
        # logger.debug("release_folder: %s, use setup: %s" % (self.release_folder, self.use_setup_name))
        return SetupDb(self.release_folder, use_setup_name=self.use_setup_name)

    def load_from_db(self, db_path: str | None = None) -> None:
        """Load/reload the setting from the setup db"""
        # logger.info("*** > SETUP: loading ...")

        # try:
        if db_path is None:
            db = self.db
        else:
            logger.debug("loading db from %s" % db_path)
            release_folder, _ = os.path.split(db_path)
            db = SetupDb(release_folder)

        if db.setup_version > self.SUPPORTED_VERSION:
            raise RuntimeError("unsupported setup version: %s" % db.setup_version)

        self.setup_version = db.setup_version
        self.setup_id = db.active_setup_id
        self.setup_name = db.setup_name

        # input
        self.use_woa09 = db.use_woa09
        self.use_woa13 = db.use_woa13
        self.use_woa18 = db.use_woa18
        self.use_woa23 = db.use_woa23
        self.use_rtofs = db.use_rtofs
        self.use_gomofs = db.use_gomofs
        self.ssp_extension_source = Dicts.atlases[db.ssp_extension_source]
        self.ssp_salinity_source = Dicts.atlases[db.ssp_salinity_source]
        self.ssp_temp_sal_source = Dicts.atlases[db.ssp_temp_sal_source]
        self.ssp_up_or_down = Dicts.ssp_directions[db.ssp_up_or_down]
        self.rx_max_wait_time = db.rx_max_wait_time
        self.use_sis4 = db.use_sis4
        self.use_sis5 = db.use_sis5
        self.use_sippican = db.use_sippican
        self.use_nmea_0183 = db.use_nmea_0183
        self.use_mvp = db.use_mvp

        # output
        # client list
        self.client_list = ClientList()  # to reset the list
        for client in db.client_list:
            client_string = "%s:%s:%s:%s" % (client[1], client[2], client[3], client[4])
            self.client_list.add_client(client_string)
            # logger.debug('- load: %s' % client_string)

        # listeners - sis4
        self.sis_listen_port = db.sis_listen_port
        self.sis_listen_timeout = db.sis_listen_timeout
        # output - sis 4 and 5
        self.sis_auto_apply_manual_casts = db.sis_auto_apply_manual_casts

        # listeners - sippican
        self.sippican_listen_port = db.sippican_listen_port
        self.sippican_listen_timeout = db.sippican_listen_timeout

        # listeners - nmea
        self.nmea_listen_port = db.nmea_listen_port
        self.nmea_listen_timeout = db.nmea_listen_timeout        

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
        self.server_max_failed_attempts = db.server_max_failed_attempts

        # current settings
        self.current_project = db.current_project
        self.custom_projects_folder = db.custom_projects_folder
        self.custom_outputs_folder = db.custom_outputs_folder
        self.custom_woa09_folder = db.custom_woa09_folder
        self.custom_woa13_folder = db.custom_woa13_folder
        self.custom_woa18_folder = db.custom_woa18_folder
        self.custom_woa23_folder = db.custom_woa23_folder
        self.noaa_tools = db.noaa_tools
        self.default_institution = db.default_institution
        self.default_survey = db.default_survey
        self.default_vessel = db.default_vessel
        self.average_sound_speed = db.average_sound_speed
        self.auto_apply_default_metadata = db.auto_apply_default_metadata

        db.close()

        # except Exception as e:
        #     raise RuntimeError("while loading db setup, %s" % e)

        # logger.info("*** > SETUP: loaded!")

    def save_to_db(self) -> None:
        """Save setup to db"""
        logger.info("*** > SETUP: saving ...")

        try:
            db = self.db
            # db.setup_version = self.setup_version  # not overwrite the version since it implies different tables
            # db.active_setup_id = self.setup_id  # obviously, unactivated to avoid db logic corruption
            # db.setup_status  # only the current setup is visualized
            # db.setup_name = self.setup_name

            # input
            db.use_woa09 = self.use_woa09
            db.use_woa13 = self.use_woa13
            db.use_woa18 = self.use_woa18
            db.use_woa23 = self.use_woa23
            db.use_rtofs = self.use_rtofs
            db.use_gomofs = self.use_gomofs
            db.ssp_extension_source = PkgHelper.first_match(Dicts.atlases, self.ssp_extension_source)
            db.ssp_salinity_source = PkgHelper.first_match(Dicts.atlases, self.ssp_salinity_source)
            db.ssp_temp_sal_source = PkgHelper.first_match(Dicts.atlases, self.ssp_temp_sal_source)
            db.ssp_up_or_down = PkgHelper.first_match(Dicts.ssp_directions, self.ssp_up_or_down)

            db.rx_max_wait_time = self.rx_max_wait_time
            db.use_sis4 = self.use_sis4
            db.use_sis5 = self.use_sis5
            db.use_sippican = self.use_sippican
            db.use_nmea_0183 = self.use_nmea_0183
            db.use_mvp = self.use_mvp

            # client list
            db.delete_clients()
            for client in self.client_list.clients:
                logger.debug('- save: %s' % client.name)
                db.add_client(client_name=client.name,
                              client_ip=client.ip, client_port=client.port,
                              client_protocol=client.protocol)

            # listeners - sis4
            db.sis_listen_port = self.sis_listen_port
            db.sis_listen_timeout = self.sis_listen_timeout

            # output - sis 4 and 5
            db.sis_auto_apply_manual_casts = self.sis_auto_apply_manual_casts

            # listeners - sippican
            db.sippican_listen_port = self.sippican_listen_port
            db.sippican_listen_timeout = self.sippican_listen_timeout

            # listeners - nmea
            db.nmea_listen_port = self.nmea_listen_port
            db.nmea_listen_timeout = self.nmea_listen_timeout            

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
            db.server_max_failed_attempts = self.server_max_failed_attempts

            # current settings
            db.current_project = self.current_project
            db.custom_projects_folder = self.custom_projects_folder
            db.custom_outputs_folder = self.custom_outputs_folder
            db.custom_woa09_folder = self.custom_woa09_folder
            db.custom_woa13_folder = self.custom_woa13_folder
            db.custom_woa18_folder = self.custom_woa18_folder
            db.custom_woa23_folder = self.custom_woa23_folder
            db.noaa_tools = self.noaa_tools
            db.default_institution = self.default_institution
            db.default_survey = self.default_survey
            db.default_vessel = self.default_vessel
            db.average_sound_speed = self.average_sound_speed
            db.auto_apply_default_metadata = self.auto_apply_default_metadata

            db.commit()
            db.close()

        except Exception as e:
            raise RuntimeError("while saving setup to db, %s" % e)

        logger.info("*** > SETUP: saved!")

    def __repr__(self) -> str:
        msg = "  <setup:%s:%s>\n" % (self.setup_id, self.setup_name)

        msg += "    <setup version: %s>\n" % self.setup_version

        msg += "    <input>\n"
        msg += "      <use_woa09: %s>\n" % self.use_woa09
        msg += "      <use_woa13: %s>\n" % self.use_woa13
        msg += "      <use_woa18: %s>\n" % self.use_woa18
        msg += "      <use_woa23: %s>\n" % self.use_woa23
        msg += "      <use_rtofs: %s>\n" % self.use_rtofs
        msg += "      <use_gomofs: %s>\n" % self.use_gomofs
        msg += "      <ssp_extension_source: %s>\n" % self.ssp_extension_source
        msg += "      <ssp_salinity_source: %s>\n" % self.ssp_salinity_source
        msg += "      <ssp_temp_sal_source: %s>\n" % self.ssp_temp_sal_source
        msg += "      <up_or_down: %s>\n" % self.ssp_up_or_down
        msg += "      <rx_max_wait_time: %s>\n" % self.rx_max_wait_time
        msg += "      <use_sis4: %s>\n" % self.use_sis4
        msg += "      <use_sis5: %s>\n" % self.use_sis5
        msg += "      <use_sippican: %s>\n" % self.use_sippican
        msg += "      <use_nmea_0183: %s>\n" % self.use_nmea_0183
        msg += "      <use_mvp: %s>\n" % self.use_mvp
        msg += "    <output>\n"
        msg += "      <clients>\n"
        for c in self.client_list.clients:
            msg += "        <%s>\n" % c
        msg += "    <listeners - sis>\n"
        msg += "      <sis4_listen_port: %s>\n" % self.sis_listen_port
        msg += "      <sis4_listen_timeout: %s>\n" % self.sis_listen_timeout
        msg += "      <sis_auto_apply_manual_casts: %s>\n" % self.sis_auto_apply_manual_casts
        msg += "    <listeners - sippican>\n"
        msg += "      <sippican_listen_port: %s>\n" % self.sippican_listen_port
        msg += "      <sippican_listen_timeout: %s>\n" % self.sippican_listen_timeout
        msg += "    <listeners - nmea>\n"
        msg += "      <nmea_listen_port: %s>\n" % self.nmea_listen_port
        msg += "      <nmea_listen_timeout: %s>\n" % self.nmea_listen_timeout        
        msg += "    <listeners - mvp>\n"
        msg += "      <mvp_ip_address: %s>\n" % self.mvp_ip_address
        msg += "      <mvp_listen_port: %s>\n" % self.mvp_listen_port
        msg += "    <server>\n"
        msg += "      <server_source: %s>\n" % self.server_source
        msg += "      <server_apply_surface_sound_speed: %s>\n" % self.server_apply_surface_sound_speed
        msg += "      <server_max_failed_attempts: %s>\n" % self.server_max_failed_attempts
        msg += "    <current settings>\n"
        msg += "      <current_project: %s>\n" % self.current_project
        msg += "      <projects folder: %s>\n" % self.custom_projects_folder
        msg += "      <outputs folder: %s>\n" % self.custom_outputs_folder
        msg += "      <woa09 folder: %s>\n" % self.custom_woa09_folder
        msg += "      <woa13 folder: %s>\n" % self.custom_woa13_folder
        msg += "      <woa18 folder: %s>\n" % self.custom_woa18_folder
        msg += "      <woa23 folder: %s>\n" % self.custom_woa23_folder
        msg += "      <noaa tools: %s>\n" % self.noaa_tools
        msg += "      <default_institution: %s>\n" % self.default_institution
        msg += "      <default_survey: %s>\n" % self.default_survey
        msg += "      <default_vessel: %s>\n" % self.default_vessel
        msg += "      <average sound speed: %s>\n" % self.average_sound_speed        
        msg += "      <auto_apply_default_metadata: %s>\n" % self.auto_apply_default_metadata

        return msg
