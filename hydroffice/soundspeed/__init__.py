"""
Hydro-Package
Sound Speed
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

__version__ = '2017.0.0'
__doc__ = "Sound Speed"
__author__ = 'gmasetti@ccom.unh.edu; barry.gallagher@noaa.gov; brc@ccom.unh.edu; chen.zang@noaa.gov; ' \
             'matthew.wilson@noaa.gov; jack.riley@noaa.gov'
__license__ = 'LGPLv2.1 or CCOM-UNH Industrial Associate license'
__copyright__ = 'Copyright 2017 University of New Hampshire, Center for Coastal and Ocean Mapping'


# def hyo():
# def hyo_app():
def hyo_lib():
    return __doc__, __version__
