import logging

from hyo2.abc2.lib.helper import Helper

logger = logging.getLogger(__name__)

vessel_list = [
    "RA Rainier (ship)",
    "R3 Rainier - Launch 2803",
    "R4 Rainier - Launch 2801",
    "R5 Rainier - Launch 2802",
    "R6 Rainier - Launch 2804",
    "TJ Thomas Jefferson (ship)",
    "T3 Thomas Jefferson - Launch 2903",
    "T4 Thomas Jefferson - Launch 2904",
    "BH Bay Hydro II Chesapeake Bay",
    "N1 NRT-1  Gulf Coast",
    "N2 NRT-2  Southeast",
    "N3 NRT-3  Pacific",
    "N4 NRT-4  Gulf Coast",
    "N5 NRT-5  Northeast",
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
    default_use_woa_18 = 0
    default_use_rtofs = 0
    default_use_gomofs = 0
    default_custom_woa09_folder = Helper.hstb_woa09_folder()
    default_custom_woa13_folder = Helper.hstb_woa13_folder()
    default_custom_woa18_folder = Helper.hstb_woa18_folder()
    default_noaa_tools = 1
    default_default_institution = institution_list[0]

else:
    default_use_woa_09 = 1
    default_use_woa_13 = 0
    default_use_woa_18 = 0
    default_use_rtofs = 0
    default_use_gomofs = 0
    default_custom_woa09_folder = ""
    default_custom_woa13_folder = ""
    default_custom_woa18_folder = ""
    default_noaa_tools = 0
    default_default_institution = ""

CREATE_SETTINGS = """-- noinspection SqlResolveForFile
 CREATE TABLE IF NOT EXISTS general(
     id integer PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
     setup_version integer NOT NULL DEFAULT 5,
     setup_name text NOT NULL UNIQUE DEFAULT "default",
     setup_status text NOT NULL DEFAULT "inactive",
     /* input */
     use_woa09 integer NOT NULL DEFAULT %d,
     use_woa13 integer NOT NULL DEFAULT %d,
     use_woa18 integer NOT NULL DEFAULT %d,
     use_rtofs integer NOT NULL DEFAULT %d,
     use_gomofs integer NOT NULL DEFAULT %d,     
     ssp_extension_source text NOT NULL DEFAULT "WOA09",
     ssp_salinity_source text NOT NULL DEFAULT "WOA09",
     ssp_temp_sal_source text NOT NULL DEFAULT "WOA09",
     ssp_up_or_down text NOT NULL DEFAULT "down",
     rx_max_wait_time integer NOT NULL DEFAULT 20,
     use_sis integer NOT NULL DEFAULT 1,
     use_sis5 integer NOT NULL DEFAULT 0,
     use_sippican integer NOT NULL DEFAULT 0,
     use_nmea integer NOT NULL DEFAULT 0,
     use_mvp integer NOT NULL DEFAULT 0,
     /* listeners - sis4 */
     sis_listen_port integer NOT NULL DEFAULT 16103,
     sis_listen_timeout integer NOT NULL DEFAULT 10,
     sis_auto_apply_manual_casts integer NOT NULL DEFAULT 1,
     /* listeners - sippican */
     sippican_listen_port integer NOT NULL DEFAULT 2002,
     sippican_listen_timeout integer NOT NULL DEFAULT 10,
     /* listeners - nmea */
     nmea_listen_port integer NOT NULL DEFAULT 2006,
     nmea_listen_timeout integer NOT NULL DEFAULT 10,
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
     server_max_failed_attempts integer NOT NULL DEFAULT 60,

     /* current settings */
     current_project text NOT NULL DEFAULT "default",
     custom_projects_folder text DEFAULT "",
     custom_outputs_folder text DEFAULT "",
     custom_woa09_folder text DEFAULT "%s",
     custom_woa13_folder text DEFAULT "%s",
     custom_woa18_folder text DEFAULT "%s",     
     noaa_tools integer NOT NULL DEFAULT %d,
     default_institution text NOT NULL DEFAULT "%s",
     default_survey text NOT NULL DEFAULT "",
     default_vessel text NOT NULL DEFAULT "",
     auto_apply_default_metadata integer NOT NULL DEFAULT 1
     ) """ % (default_use_woa_09, default_use_woa_13, default_use_woa_18,
              default_use_rtofs, default_use_gomofs,
              default_custom_woa09_folder, default_custom_woa13_folder, default_custom_woa18_folder,
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
     ON DELETE CASCADE
     ) """

CREATE_SETTINGS_VIEW = """-- noinspection SqlResolveForFile
 CREATE VIEW IF NOT EXISTS settings_view AS
    SELECT * FROM general g
    LEFT OUTER JOIN client_list c ON g.id=c.setup_id """

# RENAME TABLES/VIEWS

RENAME_SETTINGS = """-- noinspection SqlResolveForFile
    ALTER TABLE general RENAME TO general_old
    """

RENAME_CLIENT_LIST = """-- noinspection SqlResolveForFile
    ALTER TABLE client_list RENAME TO client_list_old
    """

# DROP TABLES/VIEWS

DROP_OLD_SETTINGS = """-- noinspection SqlResolveForFile
    DROP TABLE general_old
    """

DROP_OLD_CLIENT_LIST = """-- noinspection SqlResolveForFile
    DROP TABLE client_list_old
    """

DROP_SETTINGS_VIEW = """-- noinspection SqlResolveForFile
    DROP VIEW settings_view
    """

# COPY V1 -> V2

V1_V5_COPY_SETTINGS = """-- noinspection SqlResolveForFile
    INSERT INTO  general 
    (id, setup_name, setup_status, use_woa09, use_woa13, use_woa18, use_rtofs, 
    ssp_extension_source, ssp_salinity_source, ssp_temp_sal_source, ssp_up_or_down, rx_max_wait_time,
    use_sis, use_sippican, use_nmea, use_mvp, sis_listen_port, sis_listen_timeout,
    sis_auto_apply_manual_casts, sippican_listen_port, sippican_listen_timeout, nmea_listen_port,
    nmea_listen_timeout, mvp_ip_address, mvp_listen_port, mvp_listen_timeout, mvp_transmission_protocol,
    mvp_format, mvp_winch_port, mvp_fish_port, mvp_nav_port, mvp_system_port, mvp_sw_version,
    mvp_instrument_id, mvp_instrument, server_source, server_apply_surface_sound_speed, current_project,
    custom_projects_folder, custom_outputs_folder, custom_woa09_folder, custom_woa13_folder, noaa_tools,
    default_institution, default_survey, default_vessel, auto_apply_default_metadata) 
    SELECT 
    id, setup_name, setup_status, 
    CASE WHEN typeof(use_woa09) == 'text' THEN
        use_woa09 == 'True'
    ELSE
        use_woa09
    END, 
    CASE WHEN typeof(use_woa13) == 'text' THEN
        use_woa13 == 'False'
    ELSE
        use_woa13
    END, 
    CASE WHEN typeof(use_woa18) == 'text' THEN
        use_woa18 == 'False'
    ELSE
        use_woa18
    END,     
    CASE WHEN typeof(use_rtofs) == 'text' THEN
        use_rtofs == 'True'
    ELSE
        use_rtofs
    END,      
    ssp_extension_source, ssp_salinity_source, ssp_temp_sal_source, ssp_up_or_down, rx_max_wait_time,
    CASE WHEN typeof(use_sis) == 'text' THEN
        use_sis == 'True'
    ELSE
        use_sis
    END,
    CASE WHEN typeof(use_sippican) == 'text' THEN
        use_sippican == 'True'
    ELSE
        use_sippican
    END,
    CASE WHEN typeof(use_nmea) == 'text' THEN
        use_nmea == 'True'
    ELSE
        use_nmea
    END,
    CASE WHEN typeof(use_mvp) == 'text' THEN
        use_mvp == 'True'
    ELSE
        use_mvp
    END,
    sis_listen_port, sis_listen_timeout,
    CASE WHEN typeof(sis_auto_apply_manual_casts) == 'text' THEN
        sis_auto_apply_manual_casts == 'True'
    ELSE
        sis_auto_apply_manual_casts
    END, 
    sippican_listen_port, sippican_listen_timeout, 
    nmea_listen_port, nmea_listen_timeout, 
    mvp_ip_address, mvp_listen_port, mvp_listen_timeout, mvp_transmission_protocol, mvp_format, mvp_winch_port,
    mvp_fish_port, mvp_nav_port, mvp_system_port, mvp_sw_version, mvp_instrument_id, mvp_instrument,
    server_source, 
    CASE WHEN typeof(server_apply_surface_sound_speed) == 'text' THEN
        server_apply_surface_sound_speed == 'True'
    ELSE
        server_apply_surface_sound_speed
    END, 
    current_project, custom_projects_folder,
    custom_outputs_folder, custom_woa09_folder, custom_woa13_folder, 
    CASE WHEN typeof(noaa_tools) == 'text' THEN
        noaa_tools == 'True'
    ELSE
        noaa_tools
    END, 
    default_institution,
    default_survey, default_vessel, 
    CASE WHEN typeof(auto_apply_default_metadata) == 'text' THEN
        auto_apply_default_metadata == 'True'
    ELSE
        auto_apply_default_metadata
    END
    FROM general_old
    """

V1_V5_COPY_CLIENT_LIST = """-- noinspection SqlResolveForFile
    INSERT INTO client_list (id, setup_id, name, ip, port, protocol) 
    SELECT 
    id, setup_id, name, ip, port, protocol
    FROM client_list_old
    """
