from __future__ import absolute_import, division, print_function, unicode_literals

import os

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)


from hydroffice.soundspeed.profile.oceanography import Oceanography as Oc

# check values from Fofonoff and Millard(1983)
d_ck = 9712.653  # m
p_ck = 10000  # dBar
lat_ck = 30.0


d_calc = Oc.p2d(p=p_ck, lat=lat_ck)
logger.info("Depth: %.3f <> %.3f" % (d_calc, d_ck))
p_calc = Oc.d2p(d=d_calc, lat=lat_ck)
logger.info("Pressure: %.3f <> %.3f" % (p_calc, p_ck))

# check values dBar from Wong and Zhu(1995), Table III
s_ck = 35  # ppt
t_ck = 20  # deg C
vs_check = 1697.198  # m/sec
vs_calc = Oc.speed(d=d_ck, t=t_ck, s=s_ck, lat=lat_ck)
logger.info("Speed: %.3f <> %.3f" % (vs_calc, vs_check))
s_calc = Oc.sal(d=d_ck, speed=vs_calc, t=t_ck, lat=lat_ck)
logger.info("Salinity: %.3f <> %.3f" % (s_calc, s_ck))
