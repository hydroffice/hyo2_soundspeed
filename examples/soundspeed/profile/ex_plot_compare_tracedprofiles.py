import os
from datetime import datetime
import numpy as np

from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeed.profile.profile import Profile
from hyo.soundspeed.profile.profilelist import ProfileList
from hyo.soundspeed.profile.ray_tracing.tracedprofile import TracedProfile
from hyo.soundspeed.profile.ray_tracing.diff_tracedprofiles import DiffTracedProfiles
from hyo.soundspeed.profile.ray_tracing.plot_tracedprofiles import PlotTracedProfiles


# create an example profile for testing
def make_fake_ssp(bias=0.0):

    ssp = Profile()
    d = np.arange(0.0, 1000.0, 5.0)
    vs = np.arange(1480.0 + bias, 1520.0 + bias, 0.2)
    t = np.arange(0.0, 100.0, 0.5)
    s = np.arange(0.0, 100.0, 0.5)
    ssp.init_proc(d.size)
    ssp.proc.depth = d
    ssp.proc.speed = vs
    ssp.proc.temp = t
    ssp.proc.sal = s
    ssp.meta.latitude = 43.13555
    ssp.meta.longitude = -70.9395
    ssp.meta.utc_time = datetime.utcnow()
    return ssp


avg_depth = 10000.0  # just a very deep value
half_swath_angle = 70.0  # a safely large angle

ssp1 = make_fake_ssp(bias=0.0)
ssp1_list = ProfileList()
ssp1_list.append_profile(ssp1)
tp1 = TracedProfile(ssp=ssp1_list, avg_depth=avg_depth,
                    half_swath=half_swath_angle)

ssp2 = make_fake_ssp(bias=10.0)
ssp2_list = ProfileList()
ssp2_list.append_profile(ssp2)
tp2 = TracedProfile(ssp=ssp2_list, avg_depth=avg_depth,
                    half_swath=half_swath_angle)

diff = DiffTracedProfiles(old_tp=tp1, new_tp=tp2)
diff.calc_diff()

start_time = datetime.now()
plot = PlotTracedProfiles(diff_tps=diff)
plot.make_comparison_plots()
end_time = datetime.now()
logger.debug("timing: %s" % (end_time - start_time))
