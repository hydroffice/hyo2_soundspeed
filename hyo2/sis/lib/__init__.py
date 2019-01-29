"""
Hydro-Package
Sound Speed
"""

import os
from hyo2.abc.lib.lib_info import LibInfo
from hyo2.sis import name, __version__
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

lib_info = LibInfo()

lib_info.lib_name = name
lib_info.lib_version = __version__
lib_info.lib_author = "Giuseppe Masetti(UNH,CCOM)"
lib_info.lib_author_email = "gmasetti@ccom.unh.edu"

lib_info.lib_license = "LGPLv3"
lib_info.lib_license_url = "https://www.hydroffice.org/license/"

lib_info.lib_path = os.path.abspath(os.path.dirname(__file__))

lib_info.lib_url = "https://www.hydroffice.org/soundspeed/"
lib_info.lib_manual_url = "https://www.hydroffice.org/manuals/soundspeed/index.html"
lib_info.lib_support_email = "sis@hydroffice.org"
lib_info.lib_latest_url = "https://www.hydroffice.org/latest/soundspeed.txt"

lib_info.lib_dep_dict = {
    "hyo2.abc": "hyo2.abc",
    "PySide2": "PySide2"
}
