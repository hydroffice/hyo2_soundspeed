import pyximport
pyximport.install()
import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

import os
from datetime import datetime
import numpy as np

from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeed.profile.profile import Profile
from hyo.soundspeed.profile.dicts import Dicts
from hyo.soundspeed.profile.profilelist import ProfileList
from hyo.soundspeed.profile.ray_tracing.tracedprofile import TracedProfile


# create an example profile for testing
def fresh_profile(bias=0.0):
    ssp = Profile()
    d = np.arange(0.0, 100.0, 0.5)
    vs = np.arange(1450.0 + bias, 1550.0 + bias, 0.5)
    t = np.arange(0.0, 100.0, 0.5)
    s = np.arange(0.0, 100.0, 0.5)
    ssp.init_proc(d.size)
    ssp.proc.depth = d
    ssp.proc.speed = vs
    ssp.proc.temp = t
    ssp.proc.sal = s
    ssp.proc.flag[40:50] = Dicts.flags['user']
    ssp.proc.flag[50:70] = Dicts.flags['filtered']
    ssp.meta.latitude = 43.13555
    ssp.meta.longitude = -70.9395
    ssp.meta.utc_time = datetime.utcnow()
    return ssp


tss_depth = 5.0
tss_value = 1500.0
avg_depth = 1000.0
half_swath_angle = 70.0
ssp = fresh_profile()
ssp_list = ProfileList()
ssp_list.append_profile(ssp)

profile = TracedProfile(tss_depth=tss_depth, tss_value=tss_value,
                        avg_depth=avg_depth, half_swath=half_swath_angle,
                        ssp=ssp_list)

logger.debug("traced profile:\n%s" % profile)
