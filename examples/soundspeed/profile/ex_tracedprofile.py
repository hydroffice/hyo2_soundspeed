import pyximport
pyximport.install()
import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

import logging

from datetime import datetime
import numpy as np
from matplotlib import pyplot as plt

from hyo2.abc.lib.logging import set_logging
from hyo2.soundspeed.profile.profile import Profile
from hyo2.soundspeed.profile.dicts import Dicts
from hyo2.soundspeed.profile.profilelist import ProfileList
from hyo2.soundspeed.profile.ray_tracing.tracedprofile import TracedProfile


logger = logging.getLogger(__name__)
set_logging()


# create an example profile for testing
def make_fake_ssp(bias=0.0):
    p = Profile()
    d = np.arange(0.0, 100.0, 0.5)
    vs = np.arange(1450.0 + bias, 1550.0 + bias, 0.5)
    t = np.arange(0.0, 100.0, 0.5)
    s = np.arange(0.0, 100.0, 0.5)
    p.init_proc(d.size)
    p.proc.depth = d
    p.proc.speed = vs
    p.proc.temp = t
    p.proc.sal = s
    p.proc.flag[40:50] = Dicts.flags['user']
    p.proc.flag[50:70] = Dicts.flags['filtered']
    p.meta.latitude = 43.13555
    p.meta.longitude = -70.9395
    p.meta.utc_time = datetime.utcnow()
    return p


tss_depth = 5.0
tss_value = 1500.0
avg_depth = 1000.0
half_swath_angle = 65.0
ssp = make_fake_ssp(bias=0.0)
ssp_list = ProfileList()
ssp_list.append_profile(ssp)
ssp_list.debug_plot()
plt.show()

start_time = datetime.now()
profile = TracedProfile(tss_depth=tss_depth, tss_value=tss_value,
                        avg_depth=avg_depth, # half_swath=half_swath_angle,
                        ssp=ssp_list.cur)
end_time = datetime.now()
logger.debug("timing: %s" % (end_time - start_time))

logger.debug("traced profile:\n%s" % profile)
logger.debug("api:\n%s" % dir(profile))
logger.debug("rays:\n%s" % profile.str_rays())
