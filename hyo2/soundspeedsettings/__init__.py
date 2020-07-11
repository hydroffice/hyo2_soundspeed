"""
Hydro-Package
Sound Speed Settings
"""
import logging
import os

from hyo2.abc.app.app_info import AppInfo

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

name = "Sound Speed Settings"
__version__ = '2020.0.3'
__copyright__ = 'Copyright 2020 University of New Hampshire, Center for Coastal and Ocean Mapping'

app_info = AppInfo()

app_info.app_name = name
app_info.app_version = __version__
app_info.app_author = "Giuseppe Masetti(UNH,CCOM); Barry Gallagher(NOAA,OCS); " \
                      "Chen Zhang(NOAA,OCS); Matthew Sharr(NOAA,OCS); Michael Smith(UNH,CCOM)"
app_info.app_author_email = "gmasetti@ccom.unh.edu; barry.gallagher@noaa.gov; " \
                            "chen.zhang@noaa.gov; matthew.sharr@noaa.gov; msmith@ccom.unh.edu"

app_info.app_license = "LGPLv2.1 or CCOM-UNH Industrial Associate license"
app_info.app_license_url = "https://www.hydroffice.org/license/"

app_info.app_path = os.path.abspath(os.path.dirname(__file__))

app_info.app_url = "https://www.hydroffice.org/soundspeed/"
app_info.app_manual_url = "https://www.hydroffice.org/manuals/soundspeed/index.html"
app_info.app_support_email = "soundspeedmanager@hydroffice.org"
app_info.app_latest_url = "https://www.hydroffice.org/latest/soundspeedmanager.txt"

app_info.app_media_path = os.path.join(app_info.app_path, "media")
app_info.app_main_window_object_name = "MainWindow"
app_info.app_license_path = os.path.join(app_info.app_media_path, "LICENSE")
app_info.app_icon_path = os.path.join(app_info.app_media_path, "app_icon.png")

# icon size
app_info.app_tabs_icon_size = 36
app_info.app_toolbars_icon_size = 24
