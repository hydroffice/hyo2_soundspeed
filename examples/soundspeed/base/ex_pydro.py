import os
from hydroffice.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hydroffice.soundspeed.base import helper

print("> is Pydro: %s" % helper.is_pydro())

print("> HSTB folder: %s" % helper.hstb_folder())

print("> atlases folder: %s" % helper.hstb_atlases_folder())

print("> WOA09 folder: %s" % helper.hstb_woa09_folder())

print("> WOA13 folder: %s" % helper.hstb_woa13_folder())
