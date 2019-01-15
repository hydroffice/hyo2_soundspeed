import os
import logging
import sqlite3

from hyo2.abc.lib.helper import Helper
from hyo2.soundspeed.base.basedb import BaseDb
from hyo2.soundspeed.base.setup_sql import CREATE_SETTINGS, CREATE_SETTINGS_VIEW, CREATE_CLIENT_LIST

logger = logging.getLogger(__name__)


class SetupDb(BaseDb):

    def __init__(self, data_folder, db_file="setup.db", use_setup_name=None):
        self.data_folder = data_folder
        db_path = os.path.join(data_folder, db_file)
        super(SetupDb, self).__init__(db_path=db_path)
        is_new_db = not os.path.exists(db_path)
        self.reconnect_or_create()
        self._check_default_setup()
        self.use_setup_name = use_setup_name

    def build_tables(self):
        if not self.conn:
            logger.error("Missing db connection")
            return False

        try:
            with self.conn:
                if self.conn.execute(""" PRAGMA foreign_keys """):
                    # logger.info("foreign keys active")
                    pass
                else:
                    logger.error("foreign keys not active")
                    return False
                self.conn.execute(CREATE_SETTINGS)
                self.conn.execute(CREATE_CLIENT_LIST)
                self.conn.execute(CREATE_SETTINGS_VIEW)
            return True

        except sqlite3.Error as e:
            logger.error("during building tables, %s: %s" % (type(e), e))
            return False

    def open_folder(self):
        Helper.explore_folder(self.data_folder)

    # --- setup stuff
    
    def _check_default_setup(self):
        """Check for the presence of default settings, creating them if missing and not other setups. """
        if len(self.setup_list) == 0:
            logger.debug("creating default setup")
            default_setup = "default"
            if not self.setup_exists(default_setup):
                self.add_setup(setup_name=default_setup)
                self.activate_setup(setup_name=default_setup)

    # noinspection SqlResolve
    def setup_exists(self, setup_name):
        """Check if the passed profile exists"""
        try:
            ret = self.conn.execute(""" SELECT COUNT(id) FROM general WHERE setup_name=? """,
                                    (setup_name,)).fetchone()
            # logger.info("found %d settings named %s" % (ret[0], setup_name))
            if ret[0] == 0:
                return False
            else:
                return True
        except sqlite3.Error as e:
            raise RuntimeError("%s: %s" % (type(e), e))

    # noinspection SqlResolve
    def add_setup(self, setup_name):
        """ Add setting with passed name and default values."""
        with self.conn:
            try:
                logger.info("inserting %s settings with default values" % setup_name)
                # create a default settings record
                self.conn.execute(""" INSERT INTO general (setup_name) VALUES(?) """, (setup_name,))

                # retrieve settings id
                ret = self.conn.execute(""" SELECT id FROM general WHERE setup_name=? """,
                                        (setup_name,)).fetchone()
                # logger.info("%s settings id: %s" % (setup_name, ret[0]))

                # add default client list
                self.conn.execute(""" INSERT INTO client_list (setup_id) VALUES(?) """, (ret[0], ))
                # logger.info("inserted %s settings values" % setup_name)

                return True
   
            except sqlite3.Error as e:
                logger.error("%s: %s" % (type(e), e))
                return False

    # noinspection SqlResolve
    def delete_setup(self, setup_name):
        """ Delete a profile (if not active)."""
        with self.conn:
            try:
                # check if active
                ret = self.conn.execute(""" SELECT setup_status FROM general WHERE setup_name=? """,
                                        (setup_name,)).fetchone()
                # logger.info("%s settings status: %s" % (setup_name, ret))
                if ret == "active":
                    raise RuntimeError("Attempt to delete active profile (%s)" % setup_name)
   
                # create a default settings record
                self.conn.execute(""" DELETE FROM general WHERE setup_name=? """, (setup_name,))
                # logger.info("deleted profile: %s" % setup_name)
   
            except sqlite3.Error as e:
                logger.error("%s: %s" % (type(e), e))
                return False

    # noinspection SqlResolve
    def activate_setup(self, setup_name):
        """Activate a profile, if it exists"""
        if not self.setup_exists(setup_name):
            return False
   
        with self.conn:
            try:
                # set all the values to inactive
                self.conn.execute(""" UPDATE general SET setup_status="inactive" """)
                # set active just the passed profile
                self.conn.execute(""" UPDATE general SET setup_status="active" WHERE setup_name=? """, (setup_name, ))
                # logger.info("activated profile: %s" % setup_name)
            except sqlite3.Error as e:
                logger.error("%s: %s" % (type(e), e))
                return False

    # noinspection SqlResolve
    @property
    def active_setup_id(self):
        """ Retrieve the active settings id """
        if self.use_setup_name is None:
            ret = self.conn.execute(""" SELECT id FROM general WHERE setup_status="active" """).fetchone()
            return ret[0]

        # logger.debug('using setup name: %s' % self.use_setup_name)
        ret = self.conn.execute(""" SELECT id FROM general WHERE setup_name=? """,
                                (self.use_setup_name, )).fetchone()
        return ret[0]

    # noinspection SqlResolve
    def setup_id_from_setup_name(self, setup_name):
        ret = self.conn.execute(""" SELECT id FROM general WHERE setup_name=? """,
                                (setup_name, )).fetchone()
        return ret[0]

    # --- clients list

    # noinspection SqlResolve
    @property
    def client_list(self):
        ret = self.conn.execute(""" SELECT id, name, ip, port, protocol FROM client_list WHERE setup_id=? """,
                                (self.active_setup_id,)).fetchall()
        # logger.info("SSP clients: %s" % len(ret))
        return ret

    # noinspection SqlResolve
    def client_exists(self, client_name):
        """Check if the passed profile exists"""
        try:
            ret = self.conn.execute(""" SELECT COUNT(id) FROM client_list WHERE name=? """,
                                    (client_name,)).fetchone()
            # logger.info("found %s clients named %s" % (ret[0], client_name))
            if ret[0] == 0:
                return False
            else:
                return True
        except sqlite3.Error as e:
            raise RuntimeError("%s: %s" % (type(e), e))

    # noinspection SqlResolve
    def add_client(self, client_name, client_ip="127.0.0.1", client_port=4001, client_protocol="SIS"):
        """Add client with passed name and default values."""
        with self.conn:
            try:
                self.conn.execute(""" INSERT INTO client_list (setup_id, name, ip, port, protocol)
                                                  VALUES(?, ?, ?, ?, ?) """,
                                  (self.active_setup_id, client_name, client_ip, client_port, client_protocol))
                # logger.info("inserted %s client values" % client_name, client_ip, client_port, client_protocol)

            except sqlite3.Error as e:
                logger.error("%s: %s" % (type(e), e))
                return False

    # noinspection SqlResolve
    def delete_client(self, client_name):
        """Delete a client."""
        with self.conn:
            try:
                self.conn.execute(""" DELETE FROM client_list WHERE name=? AND setup_id=?""",
                                  (client_name, self.active_setup_id,))
                # logger.info("deleted client: %s" % client_name)

            except sqlite3.Error as e:
                logger.error("%s: %s" % (type(e), e))
                return False

    # noinspection SqlResolve
    def delete_clients(self):
        """Delete all clients."""
        with self.conn:
            try:
                self.conn.execute(""" DELETE FROM client_list WHERE setup_id=?""",
                                  (self.active_setup_id,))
                # logger.info("deleted clients")

            except sqlite3.Error as e:
                logger.error("%s: %s" % (type(e), e))
                return False

    # --- setup list

    # noinspection SqlResolve
    @property
    def setup_list(self):
        ret = self.conn.execute(""" SELECT id, setup_name, setup_status, setup_version FROM general """).fetchall()
        # logger.info("Profiles list: %s" % len(ret))
        return ret

    # --- templates
    def _getter_int(self, attrib):
        r = self.conn.execute(""" SELECT """ + attrib + """ FROM general WHERE id=? """,
                              (self.active_setup_id,)).fetchone()
        # logger.info("%s = %d" % (attrib, r[0]))
        return r[0]

    def _setter_int(self, attrib, value):
        with self.conn:
            try:
                self.conn.execute(""" UPDATE general SET """ + attrib + """=? WHERE id=? """,
                                  (value, self.active_setup_id,))
            except sqlite3.Error as e:
                logger.error("while setting %s, %s: %s" % (attrib, type(e), e))
        # logger.info("%s = %d" % (attrib, value))

    def _getter_str(self, attrib):
        r = self.conn.execute(""" SELECT """ + attrib + """ FROM general WHERE id=? """,
                              (self.active_setup_id,)).fetchone()
        # logger.info("%s = %s" % (attrib, r[0]))
        return r[0]

    def _setter_str(self, attrib, value):
        with self.conn:
            try:
                self.conn.execute(""" UPDATE general SET """ + attrib + """=? WHERE id=? """,
                                  (value, self.active_setup_id,))
            except sqlite3.Error as e:
                logger.error("while setting %s, %s: %s" % (attrib, type(e), e))
        # logger.info("%s = %s" % (attrib, value))

    def _getter_bool(self, attrib):
        r = self.conn.execute(""" SELECT """ + attrib + """ FROM general WHERE id=? """,
                              (self.active_setup_id,)).fetchone()
        # logger.info("%s = %s" % (attrib, r[0]))
        if isinstance(r[0], str):
            return r[0] == "True"
        else:
            return r[0] == 1

    def _setter_bool(self, attrib, value):

        if type(value) is not bool:
            logger.error("passed a %s in place of a boolean" % type(value))
            return

        # required to check whether we are using the old str boolean
        r = self.conn.execute(""" SELECT """ + attrib + """ FROM general WHERE id=? """,
                              (self.active_setup_id,)).fetchone()
        # logger.info("%s = %s" % (attrib, r[0]))
        if isinstance(r[0], str):
            is_str = True
        else:
            is_str = False

        with self.conn:
            if value:
                if is_str:
                    value = "True"
                else:
                    value = 1
            else:
                if is_str:
                    value = "False"
                else:
                    value = 0

            try:
                self.conn.execute(""" UPDATE general SET """ + attrib + """=? WHERE id=? """,
                                  (value, self.active_setup_id,))
            except sqlite3.Error as e:
                logger.error("while setting %s, %s: %s" % (attrib, type(e), e))
        # logger.info("%s = %s" % (attrib, value))

    # --- active library version
    @property
    def setup_version(self):
        return self._getter_int("setup_version")

    @setup_version.setter
    def setup_version(self, value):
        self._setter_int("setup_version", value)

    # --- active setup name
    @property
    def setup_name(self):
        return self._getter_str("setup_name")

    @setup_name.setter
    def setup_name(self, value):
        self._setter_str("setup_name", value)

    # --- active setup status
    @property
    def setup_status(self):
        return self._getter_str("setup_status")

    # --- use_woa09
    @property
    def use_woa09(self):
        return self._getter_bool("use_woa09")

    @use_woa09.setter
    def use_woa09(self, value):
        self._setter_bool("use_woa09", value)

    # --- use_woa13
    @property
    def use_woa13(self):
        return self._getter_bool("use_woa13")

    @use_woa13.setter
    def use_woa13(self, value):
        self._setter_bool("use_woa13", value)

    # --- use_rtofs
    @property
    def use_rtofs(self):
        return self._getter_bool("use_rtofs")

    @use_rtofs.setter
    def use_rtofs(self, value):
        self._setter_bool("use_rtofs", value)

    # --- ssp_extension_source
    @property
    def ssp_extension_source(self):
        return self._getter_str("ssp_extension_source")

    @ssp_extension_source.setter
    def ssp_extension_source(self, value):
        self._setter_str("ssp_extension_source", value)

    # --- ssp_salinity_source
    @property
    def ssp_salinity_source(self):
        return self._getter_str("ssp_salinity_source")

    @ssp_salinity_source.setter
    def ssp_salinity_source(self, value):
        self._setter_str("ssp_salinity_source", value)

    # --- ssp_temp_sal_source
    @property
    def ssp_temp_sal_source(self):
        return self._getter_str("ssp_temp_sal_source")

    @ssp_temp_sal_source.setter
    def ssp_temp_sal_source(self, value):
        self._setter_str("ssp_temp_sal_source", value)

    # --- ssp_up_or_down
    @property
    def ssp_up_or_down(self):
        return self._getter_str("ssp_up_or_down")

    @ssp_up_or_down.setter
    def ssp_up_or_down(self, value):
        self._setter_str("ssp_up_or_down", value)

    # --- use_sis
    @property
    def use_sis(self):
        return self._getter_bool("use_sis")

    @use_sis.setter
    def use_sis(self, value):
        self._setter_bool("use_sis", value)

    # --- use_sippican
    @property
    def use_sippican(self):
        return self._getter_bool("use_sippican")

    @use_sippican.setter
    def use_sippican(self, value):
        self._setter_bool("use_sippican", value)

    # --- use_mvp
    @property
    def use_mvp(self):
        return self._getter_bool("use_mvp")

    @use_mvp.setter
    def use_mvp(self, value):
        self._setter_bool("use_mvp", value)

    # --- rx_max_wait_time
    @property
    def rx_max_wait_time(self):
        return self._getter_int("rx_max_wait_time")

    @rx_max_wait_time.setter
    def rx_max_wait_time(self, value):
        self._setter_int("rx_max_wait_time", value)

    # --- log_user
    @property
    def log_user(self):
        return self._getter_bool("log_user")

    @log_user.setter
    def log_user(self, value):
        self._setter_bool("log_user", value)

    # --- log_server
    @property
    def log_server(self):
        return self._getter_bool("log_server")

    @log_server.setter
    def log_server(self, value):
        self._setter_bool("log_server", value)

    # --- sis_listen_port
    @property
    def sis_listen_port(self):
        return self._getter_int("sis_listen_port")

    @sis_listen_port.setter
    def sis_listen_port(self, value):
        self._setter_int("sis_listen_port", value)

    # --- sis_listen_timeout
    @property
    def sis_listen_timeout(self):
        return self._getter_int("sis_listen_timeout")

    @sis_listen_timeout.setter
    def sis_listen_timeout(self, value):
        self._setter_int("sis_listen_timeout", value)

    # --- sis_auto_apply_manual_casts
    @property
    def sis_auto_apply_manual_casts(self):
        return self._getter_bool("sis_auto_apply_manual_casts")

    @sis_auto_apply_manual_casts.setter
    def sis_auto_apply_manual_casts(self, value):
        self._setter_bool("sis_auto_apply_manual_casts", value)

    # --- sippican_listen_port
    @property
    def sippican_listen_port(self):
        return self._getter_int("sippican_listen_port")

    @sippican_listen_port.setter
    def sippican_listen_port(self, value):
        self._setter_int("sippican_listen_port", value)

    # --- sippican_listen_timeout
    @property
    def sippican_listen_timeout(self):
        return self._getter_int("sippican_listen_timeout")

    @sippican_listen_timeout.setter
    def sippican_listen_timeout(self, value):
        self._setter_int("sippican_listen_timeout", value)

    # --- mvp_ip_address
    @property
    def mvp_ip_address(self):
        return self._getter_str("mvp_ip_address")

    @mvp_ip_address.setter
    def mvp_ip_address(self, value):
        self._setter_str("mvp_ip_address", value)

    # --- mvp_listen_port
    @property
    def mvp_listen_port(self):
        return self._getter_int("mvp_listen_port")

    @mvp_listen_port.setter
    def mvp_listen_port(self, value):
        self._setter_int("mvp_listen_port", value)

    # --- mvp_listen_timeout
    @property
    def mvp_listen_timeout(self):
        return self._getter_int("mvp_listen_timeout")

    @mvp_listen_timeout.setter
    def mvp_listen_timeout(self, value):
        self._setter_int("mvp_listen_timeout", value)

    # --- mvp_transmission_protocol
    @property
    def mvp_transmission_protocol(self):
        return self._getter_str("mvp_transmission_protocol")

    @mvp_transmission_protocol.setter
    def mvp_transmission_protocol(self, value):
        self._setter_str("mvp_transmission_protocol", value)

    # --- mvp_format
    @property
    def mvp_format(self):
        return self._getter_str("mvp_format")

    @mvp_format.setter
    def mvp_format(self, value):
        self._setter_str("mvp_format", value)

    # --- mvp_winch_port
    @property
    def mvp_winch_port(self):
        return self._getter_int("mvp_winch_port")

    @mvp_winch_port.setter
    def mvp_winch_port(self, value):
        self._setter_int("mvp_winch_port", value)

    # --- mvp_fish_port
    @property
    def mvp_fish_port(self):
        return self._getter_int("mvp_fish_port")

    @mvp_fish_port.setter
    def mvp_fish_port(self, value):
        self._setter_int("mvp_fish_port", value)

    # --- mvp_nav_port
    @property
    def mvp_nav_port(self):
        return self._getter_int("mvp_nav_port")

    @mvp_nav_port.setter
    def mvp_nav_port(self, value):
        self._setter_int("mvp_nav_port", value)

    # --- mvp_system_port
    @property
    def mvp_system_port(self):
        return self._getter_int("mvp_system_port")

    @mvp_system_port.setter
    def mvp_system_port(self, value):
        self._setter_int("mvp_system_port", value)

    # --- mvp_sw_version
    @property
    def mvp_sw_version(self):
        return self._getter_str("mvp_sw_version")

    @mvp_sw_version.setter
    def mvp_sw_version(self, value):
        self._setter_str("mvp_sw_version", value)

    # --- mvp_instrument
    @property
    def mvp_instrument(self):
        return self._getter_str("mvp_instrument")

    @mvp_instrument.setter
    def mvp_instrument(self, value):
        self._setter_str("mvp_instrument", value)

    # --- mvp_instrument_id
    @property
    def mvp_instrument_id(self):
        return self._getter_str("mvp_instrument_id")

    @mvp_instrument_id.setter
    def mvp_instrument_id(self, value):
        self._setter_str("mvp_instrument_id", value)

    # --- server_source
    @property
    def server_source(self):
        return self._getter_str("server_source")

    @server_source.setter
    def server_source(self, value):
        self._setter_str("server_source", value)

    # --- server_apply_surface_sound_speed
    @property
    def server_apply_surface_sound_speed(self):
        return self._getter_bool("server_apply_surface_sound_speed")

    @server_apply_surface_sound_speed.setter
    def server_apply_surface_sound_speed(self, value):
        self._setter_bool("server_apply_surface_sound_speed", value)

    # --- current_project
    @property
    def current_project(self):
        return self._getter_str("current_project")

    @current_project.setter
    def current_project(self, value):
        self._setter_str("current_project", value)

    # --- custom_projects_folder
    @property
    def custom_projects_folder(self):
        return self._getter_str("custom_projects_folder")

    @custom_projects_folder.setter
    def custom_projects_folder(self, value):
        self._setter_str("custom_projects_folder", value)

    # --- custom_outputs_folder
    @property
    def custom_outputs_folder(self):
        return self._getter_str("custom_outputs_folder")

    @custom_outputs_folder.setter
    def custom_outputs_folder(self, value):
        self._setter_str("custom_outputs_folder", value)

    # --- custom_woa09_folder
    @property
    def custom_woa09_folder(self):
        return self._getter_str("custom_woa09_folder")

    @custom_woa09_folder.setter
    def custom_woa09_folder(self, value):
        self._setter_str("custom_woa09_folder", value)

    # --- custom_woa13_folder
    @property
    def custom_woa13_folder(self):
        return self._getter_str("custom_woa13_folder")

    @custom_woa13_folder.setter
    def custom_woa13_folder(self, value):
        self._setter_str("custom_woa13_folder", value)

    # --- noaa tools
    @property
    def noaa_tools(self):
        return self._getter_bool("noaa_tools")

    @noaa_tools.setter
    def noaa_tools(self, value):
        self._setter_bool("noaa_tools", value)

    # --- default_institution
    @property
    def default_institution(self):
        return self._getter_str("default_institution")

    @default_institution.setter
    def default_institution(self, value):
        self._setter_str("default_institution", value)

    # --- default_survey
    @property
    def default_survey(self):
        return self._getter_str("default_survey")

    @default_survey.setter
    def default_survey(self, value):
        self._setter_str("default_survey", value)

    # --- default_vessel
    @property
    def default_vessel(self):
        return self._getter_str("default_vessel")

    @default_vessel.setter
    def default_vessel(self, value):
        self._setter_str("default_vessel", value)

    # --- auto_apply_default_metadata
    @property
    def auto_apply_default_metadata(self):
        return self._getter_bool("auto_apply_default_metadata")

    @auto_apply_default_metadata.setter
    def auto_apply_default_metadata(self, value):
        self._setter_bool("auto_apply_default_metadata", value)
