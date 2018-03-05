"""
Hydro-Package
Sound Speed Settings
"""
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__version__ = '2018.1.4'
__doc__ = "Sound Speed Settings"
__author__ = 'gmasetti@ccom.unh.edu; barry.gallagher@noaa.gov; chen.zhang@noaa.gov; ' \
             'matthew.sharr@noaa.gov'
__license__ = 'LGPLv2.1 or CCOM-UNH Industrial Associate license'
__copyright__ = 'Copyright 2018 University of New Hampshire, Center for Coastal and Ocean Mapping'


def hyo_app():
    return __doc__, __version__