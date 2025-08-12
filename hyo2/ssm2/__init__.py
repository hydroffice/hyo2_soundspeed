"""
Hydro-Package
Sound Speed Manager 2
"""

import logging
import os

from hyo2.abc2.lib.package.pkg_info import PkgInfo

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

name = "Sound Speed"
__version__ = '2025.4.4'
__copyright__ = 'Copyright 2025 University of New Hampshire, Center for Coastal and Ocean Mapping'

pkg_info = PkgInfo(
    name=name,
    version=__version__,
    author="Giuseppe Masetti(UNH,JHC-CCOM); Barry Gallagher(NOAA,OCS); Chen Zhang(NOAA,OCS)",
    author_email="gmasetti@ccom.unh.edu; barry.gallagher@noaa.gov; chen.zhang@noaa.gov",
    lic="LGPLv2.1 or CCOM-UNH Industrial Associate license",
    lic_url="https://www.hydroffice.org/license/",
    path=os.path.abspath(os.path.dirname(__file__)),
    url="https://www.hydroffice.org/soundspeed/",
    manual_url="https://www.hydroffice.org/manuals/ssm2/index.html",
    support_email="soundspeed@hydroffice.org",
    latest_url="https://www.hydroffice.org/latest/soundspeed.txt",
    deps_dict={
        "hyo2.abc2": "hyo2.abc2",
        "hyo2.ssm2": "hyo2.ssm2",
        "hyo2.sdm3": "hyo2.sdm3",
        "gsw": "gsw",
        "netCDF4": "netCDF4",
        "gdal": "osgeo",
        "numpy": "numpy",
        "pyproj": "pyproj",
        "matplotlib": "matplotlib",
        "cartopy": "cartopy",
        "PySide6": "PySide6"
    }
)
