"""
Hydro-Package
Sound Speed
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

__version__ = '3.0.a1'
__doc__ = "Sound Speed"
__author__ = 'barry.gallagher@noaa.gov; jack.riley@noaa.gov; chen.zang@noaa.gov; matthew.wilson@noaa.gov; brc@ccom.unh.edu; gmasetti@ccom.unh.edu'
__license__ = 'LGPLv3 license'
__copyright__ = 'Copyright 2016 University of New Hampshire, Center for Coastal and Ocean Mapping'


# def hyo():
# def hyo_app():
def hyo_lib():
    return __doc__, __version__
