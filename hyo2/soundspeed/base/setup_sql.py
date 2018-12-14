import logging

from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


vessel_list = [
    "RA Rainier (ship)",
    "R3 Rainier - Launch 2803",
    "R4 Rainier - Launch 2801",
    "R5 Rainier - Launch 2802",
    "R6 Rainier - Launch 2804",
    "TJ Thomas Jefferson (ship)",
    "T1 Thomas Jefferson - Launch 3101",
    "T2 Thomas Jefferson - Launch 3102",
    "T3 Thomas Jefferson - Launch 2903",
    "T4 Thomas Jefferson - Launch 2904",
    "BH Bay Hydro II",
    "N1 NRT-1  Gulf",
    "N2 NRT-2  Atlantic",
    "N3 NRT-3  Pacific",
    "N4 NRT-4  Great Lakes",
    "N5 NRT-5  New York",
    "N6 NRT-6  San Francisco",
    "N7 NRT-7  Middle Atlantic",
    "FH Ferdinand R. Hassler (Ship)",
    "FA Fairweather (Ship)",
    "F5 Fairweather - Launch 2805",
    "F6 Fairweather - Launch 2806",
    "F7 Fairweather - Launch 2807",
    "F8 Fairweather - Launch 2808",
    "AR MCArthur",
    "NF Nancy Foster",
    "HI Hi'Ialakai",
    "GM Gloria Michelle",
    "EX Okeanos Explorer"
]

institution_list = [
    "NOAA Office of Coast Survey",
    "UNH CCOM/JHC"
]

if Helper.is_pydro():
    logger.debug("using pydro setup")
    default_use_woa_09 = 1
    default_use_woa_13 = 0
    default_use_rtofs = 0
    default_custom_woa09_folder = Helper.hstb_woa09_folder()
    default_custom_woa13_folder = Helper.hstb_woa13_folder()
    default_noaa_tools = 1
    default_default_institution = institution_list[0]
else:
    default_use_woa_09 = 1
    default_use_woa_13 = 0
    default_use_rtofs = 0
    default_custom_woa09_folder = ""
    default_custom_woa13_folder = ""
    default_noaa_tools = 0
    default_default_institution = ""

CREATE_SETTINGS = """-- noinspection SqlResolveForFile
 CREATE TABLE IF NOT EXISTS general(
     id integer PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
     setup_version integer NOT NULL DEFAULT 1,
     setup_name text NOT NULL UNIQUE DEFAULT "default",
     setup_status text NOT NULL DEFAULT "inactive",
     /* input */
     use_woa09 integer NOT NULL DEFAULT %d,
     use_woa13 integer NOT NULL DEFAULT %d,
     use_rtofs integer NOT NULL DEFAULT %d,
     ssp_extension_source text NOT NULL DEFAULT "WOA09",
     ssp_salinity_source text NOT NULL DEFAULT "WOA09",
     ssp_temp_sal_source text NOT NULL DEFAULT "WOA09",
     ssp_up_or_down text NOT NULL DEFAULT "down",
     rx_max_wait_time integer NOT NULL DEFAULT 20,
     use_sis integer NOT NULL DEFAULT 1,
     use_sippican integer NOT NULL DEFAULT 0,
     use_mvp integer NOT NULL DEFAULT 0,
     /* output */
     log_user integer NOT NULL DEFAULT 0,
     log_server integer NOT NULL DEFAULT 0,
     /* listeners - sis */
     sis_listen_port integer NOT NULL DEFAULT 16103,
     sis_listen_timeout integer NOT NULL DEFAULT 10,
     sis_auto_apply_manual_casts integer NOT NULL DEFAULT 1,
     /* listeners - sippican */
     sippican_listen_port integer NOT NULL DEFAULT 2002,
     sippican_listen_timeout integer NOT NULL DEFAULT 10,
     /* listeners - mvp */
     mvp_ip_address text NOT NULL DEFAULT "127.0.0.1",
     mvp_listen_port integer NOT NULL DEFAULT 2006,
     mvp_listen_timeout integer NOT NULL DEFAULT 10,
     mvp_transmission_protocol text NOT NULL DEFAULT "NAVO_ISS60",
     mvp_format text NOT NULL DEFAULT "S12",
     mvp_winch_port integer NOT NULL DEFAULT 3601,
     mvp_fish_port integer NOT NULL DEFAULT 3602,
     mvp_nav_port integer NOT NULL DEFAULT 3603,
     mvp_system_port integer NOT NULL DEFAULT 3604,
     mvp_sw_version text NOT NULL DEFAULT "2.47",
     mvp_instrument_id text NOT NULL DEFAULT "M",
     mvp_instrument text NOT NULL DEFAULT "AML_uSVPT",
     /* server */
     server_source text NOT NULL DEFAULT "WOA09",
     server_apply_surface_sound_speed integer NOT NULL DEFAULT 1,

     /* current settings */
     current_project text NOT NULL DEFAULT "default",
     custom_projects_folder text DEFAULT "",
     custom_outputs_folder text DEFAULT "",
     custom_woa09_folder text DEFAULT "%s",
     custom_woa13_folder text DEFAULT "%s",
     noaa_tools integer NOT NULL DEFAULT %d,
     default_institution text NOT NULL DEFAULT "%s",
     default_survey text NOT NULL DEFAULT "",
     default_vessel text NOT NULL DEFAULT "",
     auto_apply_default_metadata integer NOT NULL DEFAULT 1,

     /* Checks */
     CHECK (setup_status IN ("active", "inactive")),
     /* input */
     CHECK (use_woa09 IN (0, 1)),
     CHECK (use_woa13 IN (0, 1)),
     CHECK (use_rtofs IN (0, 1)),
     CHECK (ssp_extension_source IN ("RTOFS", "WOA09", "WOA13", "ref")),
     CHECK (ssp_salinity_source IN ("RTOFS", "WOA09", "WOA13", "ref")),
     CHECK (ssp_temp_sal_source IN ("RTOFS", "WOA09", "WOA13", "ref")),
     CHECK (ssp_up_or_down IN ("down", "up")),
     CHECK (rx_max_wait_time > 0),
     CHECK (use_sis IN (0, 1)),
     CHECK (use_sippican IN (0, 1)),
     CHECK (use_mvp IN (0, 1)),
     /* output */
     CHECK (log_user IN (0, 1)),
     CHECK (log_server IN (0, 1)),
     /* listeners - sis */
     CHECK (sis_listen_port > 0),
     CHECK (sis_listen_timeout > 0),
     CHECK (sis_listen_port < 65536),
     CHECK (sis_listen_timeout < 65536),
     CHECK (sis_auto_apply_manual_casts IN (0, 1)),
     /* listeners - sippican */
     CHECK (sippican_listen_port > 0),
     CHECK (sippican_listen_timeout > 0),
     /* mvp - sippican */
     CHECK (mvp_listen_port > 0),
     CHECK (mvp_listen_timeout > 0),
     CHECK (mvp_transmission_protocol IN ("NAVO_ISS60", "UNDEFINED")),
     CHECK (mvp_format IN ("S12", "CALC", "ASVP")),
     CHECK (mvp_instrument IN ("AML_uSVP", "AML_uSVPT", "AML_Smart_SVP", "AML_uCTD", "AML_uCTD+", "Valeport_SVPT", "SBE_911+", "SBE_49")),
     /* server */
     CHECK (server_source IN ("RTOFS", "WOA09", "WOA13")),
     CHECK (server_apply_surface_sound_speed IN (0, 1)),
     /* user-defined */
     CHECK (noaa_tools IN (0, 1)),
     CHECK (auto_apply_default_metadata IN (0, 1))
     ) """ % (default_use_woa_09, default_use_woa_13, default_use_rtofs,
              default_custom_woa09_folder, default_custom_woa13_folder,
              default_noaa_tools, default_default_institution)

CREATE_CLIENT_LIST = """-- noinspection SqlResolveForFile
 CREATE TABLE IF NOT EXISTS client_list(
     id integer PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
     setup_id INTEGER NOT NULL,
     name text NOT NULL DEFAULT "Local test",
     ip text NOT NULL DEFAULT "127.0.0.1",
     port integer NOT NULL DEFAULT 4001,
     protocol text NOT NULL DEFAULT "SIS",
     CONSTRAINT setup_id_fk
     FOREIGN KEY(setup_id) REFERENCES general(id)
     ON DELETE CASCADE,
     /* Checks */
     CHECK (port > 0),
     CHECK (protocol IN ("SIS", "HYPACK", "PDS2000", "QINSY"))
     ) """

CREATE_SETTINGS_VIEW = """-- noinspection SqlResolveForFile
 CREATE VIEW IF NOT EXISTS settings_view AS
    SELECT * FROM general g
    LEFT OUTER JOIN client_list c ON g.id=c.setup_id """