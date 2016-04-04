from __future__ import absolute_import, division, print_function, unicode_literals

from .. import __version__ as lib_version
import logging

logger = logging.getLogger(__name__)


CREATE_SETTINGS = """ CREATE TABLE IF NOT EXISTS general(
     id integer PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
     library_version text NOT NULL UNIQUE DEFAULT "%s",
     setup_name text NOT NULL UNIQUE DEFAULT "default",
     setup_status text NOT NULL DEFAULT "inactive",
     ssp_up_or_down text NOT NULL DEFAULT "down",
     /* rx_max_wait_time integer NOT NULL DEFAULT 30,
     ssp_extension_source text NOT NULL DEFAULT "WOA09",
     ssp_salinity_source text NOT NULL DEFAULT "WOA09",
     ssp_temp_sal_source text NOT NULL DEFAULT "WOA09",
     sis_server_source text NOT NULL DEFAULT "WOA09",
     woa_path text,
     auto_export_on_send text NOT NULL DEFAULT "False",
     auto_export_on_server_send text NOT NULL DEFAULT "True",
     user_export_prompt_filename text NOT NULL DEFAULT "False",
     user_append_caris_file text NOT NULL DEFAULT "False",
     server_append_caris_file text NOT NULL DEFAULT "False",
     km_listen_port integer NOT NULL DEFAULT 26103,
     km_listen_timeout integer NOT NULL DEFAULT 1,
     sis_auto_apply_manual_casts text NOT NULL DEFAULT "True",
     server_apply_surface_sound_speed text NOT NULL DEFAULT "True",
     sippican_listen_port integer NOT NULL DEFAULT 2002,
     sippican_listen_timeout integer NOT NULL DEFAULT 1,
     mvp_ip_address text NOT NULL DEFAULT "127.0.0.1",
     mvp_listen_port integer NOT NULL DEFAULT 2006,
     mvp_listen_timeout integer NOT NULL DEFAULT 1,
     mvp_transmission_protocol text NOT NULL DEFAULT "NAVO_ISS60",
     mvp_format text NOT NULL DEFAULT "S12",
     mvp_winch_port integer NOT NULL DEFAULT 3601,
     mvp_fish_port integer NOT NULL DEFAULT 3602,
     mvp_nav_port integer NOT NULL DEFAULT 3603,
     mvp_system_port integer NOT NULL DEFAULT 3604,
     mvp_sw_version text NOT NULL DEFAULT "2.47",
     mvp_instrument_id text NOT NULL DEFAULT "M",
     mvp_instrument text NOT NULL DEFAULT "AML_uSVPT", */
     /* Checks */
     CHECK (setup_status IN ("active", "inactive")),
     CHECK (ssp_up_or_down IN ("down", "up")) /*,
     CHECK (rx_max_wait_time > 0),
     CHECK (ssp_extension_source IN ("RTOFS", "WOA09", "WOA13")),
     CHECK (ssp_salinity_source IN ("RTOFS", "WOA09", "WOA13")),
     CHECK (ssp_temp_sal_source IN ("RTOFS", "WOA09", "WOA13")),
     CHECK (sis_server_source IN ("RTOFS", "WOA09", "WOA13")),
     CHECK (auto_export_on_send IN ("True", "False")),
     CHECK (auto_export_on_server_send IN ("True", "False")),
     CHECK (user_export_prompt_filename IN ("True", "False")),
     CHECK (user_append_caris_file IN ("True", "False")),
     CHECK (server_append_caris_file IN ("True", "False")),
     CHECK (km_listen_port > 0),
     CHECK (km_listen_timeout > 0),
     CHECK (sis_auto_apply_manual_casts IN ("True", "False")),
     CHECK (server_apply_surface_sound_speed IN ("True", "False")),
     CHECK (sippican_listen_port > 0),
     CHECK (sippican_listen_timeout > 0),
     CHECK (mvp_listen_port > 0),
     CHECK (mvp_listen_timeout > 0),
     CHECK (mvp_transmission_protocol IN ("NAVO_ISS60", "UNDEFINED")),
     CHECK (mvp_format IN ("S12", "CALC", "ASVP")),
     CHECK (mvp_instrument IN ("AML_uSVP", "AML_uSVPT", "AML_Smart_SVP", "AML_uCTD", "AML_uCTD+", "Valeport_SVPT", "SBE_911+", "SBE_49"))*/
     ) """ % lib_version

CREATE_CLIENT_LIST = """ CREATE TABLE IF NOT EXISTS client_list(
     id integer PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
     profile_id INTEGER NOT NULL,
     name text NOT NULL DEFAULT "Local test",
     ip text NOT NULL DEFAULT "127.0.0.1",
     port integer NOT NULL DEFAULT 4001,
     protocol text NOT NULL DEFAULT "SIS",
     CONSTRAINT profile_id_fk
     FOREIGN KEY(profile_id) REFERENCES general(id)
     ON DELETE CASCADE,
     /* Checks */
     CHECK (port > 0),
     CHECK (protocol IN ("SIS", "HYPACK", "PDS2000", "QINSY"))
     ) """

CREATE_SETTINGS_VIEW = """ CREATE VIEW IF NOT EXISTS settings_view AS
    SELECT * FROM general g
    LEFT OUTER JOIN client_list c ON g.id=c.profile_id """