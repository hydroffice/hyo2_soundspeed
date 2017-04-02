"""
Hydro-Package
SIS
"""

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

__version__ = '0.2.0'
__doc__ = "SIS"
__author__ = 'gmasetti@ccom.unh.edu'
__license__ = 'LGPLv3 license'
__copyright__ = 'Copyright 2016 University of New Hampshire, Center for Coastal and Ocean Mapping'


def hyo():
    return __doc__, __version__