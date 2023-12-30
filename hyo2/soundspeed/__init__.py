"""
Hydro-Package
Sound Speed
"""

import os
import logging
from hyo2.abc2.lib.lib_info import LibInfo


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

name = "Sound Speed"
__version__ = '2024.0.0'
__copyright__ = 'Copyright 2024 University of New Hampshire, Center for Coastal and Ocean Mapping'

lib_info = LibInfo()

lib_info.lib_name = name
lib_info.lib_version = __version__
lib_info.lib_author = "Giuseppe Masetti(UNH,CCOM); Barry Gallagher(NOAA,OCS); " \
                      "Chen Zhang(NOAA,OCS)"
lib_info.lib_author_email = "gmasetti@ccom.unh.edu; barry.gallagher@noaa.gov; " \
                            "chen.zhang@noaa.gov"

lib_info.lib_license = "LGPLv2.1 or CCOM-UNH Industrial Associate license"
lib_info.lib_license_url = "https://www.hydroffice.org/license/"

lib_info.lib_path = os.path.abspath(os.path.dirname(__file__))

lib_info.lib_url = "https://www.hydroffice.org/soundspeed/"
lib_info.lib_manual_url = "https://www.hydroffice.org/manuals/soundspeed/index.html"
lib_info.lib_support_email = "soundspeed@hydroffice.org"
lib_info.lib_latest_url = "https://www.hydroffice.org/latest/soundspeed.txt"

lib_info.lib_dep_dict = {
    "hyo2.abc2": "hyo2.abc2",
    "hyo2.soundspeed": "hyo2.soundspeed",
    "hyo2.surveydatamonitor": "hyo2.surveydatamonitor",
    "gsw": "gsw",
    "netCDF4": "netCDF4",
    "gdal": "osgeo",
    "numpy": "numpy",
    "pyproj": "pyproj",
    "matplotlib": "matplotlib",
    "cartopy": "cartopy",
    "PySide6": "PySide6"
}
