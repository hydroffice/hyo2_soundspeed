"""
Hydro-Package
Sound Speed
"""

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

__version__ = '2018.1.43'
__doc__ = "Sound Speed"
__author__ = 'gmasetti@ccom.unh.edu; barry.gallagher@noaa.gov; chen.zhang@noaa.gov; ' \
             'matthew.sharr@noaa.gov'
__license__ = 'LGPLv2.1 or CCOM-UNH Industrial Associate license'
__copyright__ = 'Copyright 2018 University of New Hampshire, Center for Coastal and Ocean Mapping'


def hyo_lib():
    return __doc__, __version__
