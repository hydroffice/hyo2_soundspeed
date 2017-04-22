import os

from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeed.profile.oceanography import Oceanography as Oc

# check values from Fofonoff and Millard(1983)
trusted_fof_d = 9712.653  # m
trusted_fof_lat = 30.0

# check values dBar from Wong and Zhu(1995), Table III
trusted_fof_s = 35  # ppt
trusted_fof_t = 20  # deg C
trusted_fof_vs = 1687.198  # m/sec

calc_vs = Oc.speed(d=trusted_fof_d, t=trusted_fof_t, s=trusted_fof_s, lat=trusted_fof_lat)
logger.info("Speed: %.3f <> %.3f" % (calc_vs, trusted_fof_vs))

calc_s = Oc.sal(d=trusted_fof_d, speed=calc_vs, t=trusted_fof_t, lat=trusted_fof_lat)
logger.info("Salinity: %.3f <> %.3f" % (calc_s, trusted_fof_s))
