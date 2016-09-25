"""
Hydro-Package
Sound Speed Manager
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

__version__ = '3.0.a2'
__doc__ = "Sound Speed Manager"
__author__ = 'gmasetti@ccom.unh.edu; barry.gallagher@noaa.gov; brc@ccom.unh.edu; chen.zang@noaa.gov; ' \
             'matthew.wilson@noaa.gov; jack.riley@noaa.gov'
__license__ = 'LGPLv3 license'
__copyright__ = 'Copyright 2016 University of New Hampshire, Center for Coastal and Ocean Mapping'


# def hyo():
def hyo_app():
# def hyo_lib():
    return __doc__, __version__
