"""
Hydro-Package
SIS
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

__version__ = '0.1.0'
__doc__ = "SIS"
__author__ = 'gmasetti@ccom.unh.edu'
__license__ = 'LGPLv3 license'
__copyright__ = 'Copyright 2016 University of New Hampshire, Center for Coastal and Ocean Mapping'


def hyo():
# def hyo_app():
# def hyo_lib():
    return __doc__, __version__