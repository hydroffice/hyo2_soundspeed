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
set_logging(ns_list=["hyo2.soundspeed", ])


# create an example profile for testing
def make_fake_ssp(bias=0.0, nr_samples=100):
    p = Profile()
    d = np.linspace(0.0, 16.0, nr_samples)
    vs_up = int(nr_samples / 4)
    vs_down = nr_samples - 3 * vs_up
    vs = np.concatenate([
        np.linspace(1535.0 + bias, 1532.0 + bias, vs_up),
        np.linspace(1532.0 + bias, 1528.0 + bias, vs_up),
        np.linspace(1528.0 + bias, 1523.0 + bias, vs_up),
        np.linspace(1523.0 + bias, 1500.0 + bias, vs_down)
    ])
    t = np.linspace(10.0, 20.0, nr_samples)
    s = np.linspace(34.0, 35.0, nr_samples)
    p.init_proc(d.size)
    p.proc.depth = d
    p.proc.speed = vs
    p.proc.temp = t
    p.proc.sal = s
    p.proc.flag[40:42] = Dicts.flags['user']
    p.proc.flag[50:52] = Dicts.flags['filtered']
    p.meta.latitude = 43.13555
    p.meta.longitude = -70.9395
    p.meta.utc_time = datetime.utcnow()
    return p


tss_depth = 1.0
tss_value = 1534.0
avg_depth = 100.0
half_swath_angle = 90.0
ssp = make_fake_ssp(bias=0.0)
# ssp.proc_debug_plot()
# plt.show()
ssp_list = ProfileList()
ssp_list.append_profile(ssp)

start_time = datetime.now()
profile = TracedProfile(tss_depth=tss_depth, tss_value=tss_value,
                        avg_depth=avg_depth, half_swath=half_swath_angle,
                        ssp=ssp_list.cur)
end_time = datetime.now()
logger.debug("timing: %s" % (end_time - start_time))

logger.debug("traced profile:\n%s" % profile)
# profile.debug_rays(ray_idx=45)
profile.debug_plot(ray_idx=90)
plt.show()
