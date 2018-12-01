from datetime import datetime
import random
import logging

import numpy as np

from hyo2.soundspeed.profile.profile import Profile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def fresh_profile():
    ssp = Profile()
    d = [random.gauss(val, .2) for val in np.arange(1.0, 51.0, 0.5)]
    vs = [random.gauss(val, 5.0) for val in np.arange(1450.0, 1550.0, 1.0)]
    t = [random.gauss(val, .2) for val in np.arange(15.0, 25.0, 0.1)]
    s = [random.gauss(val, .1) for val in np.arange(10.0, 60.0, 0.5)]
    ssp.init_proc(len(d))
    ssp.proc.depth = np.array(d)
    ssp.proc.speed = np.array(vs)
    ssp.proc.temp = np.array(t)
    ssp.proc.sal = np.array(s)
    # ssp.proc.flag[40:50] = 1
    # ssp.proc.flag[50:70] = 2
    ssp.meta.latitude = 43.13555
    ssp.meta.longitude = -70.9395
    ssp.meta.utc_time = datetime.utcnow()
    return ssp


ssp = fresh_profile()
logger.debug("min: %s %s %s %s" %
             (ssp.proc_depth_min, ssp.proc_speed_min,
             ssp.proc_temp_min, ssp.proc_sal_min))
logger.debug("max: %s %s %s %s" %
             (ssp.proc_depth_max, ssp.proc_speed_max,
             ssp.proc_temp_max, ssp.proc_sal_max))
logger.debug("median: %s %s %s %s" %
             (ssp.proc_depth_median, ssp.proc_speed_median,
             ssp.proc_temp_median, ssp.proc_sal_median))
logger.debug("avg: %s %s %s %s" %
             (ssp.proc_depth_mean, ssp.proc_speed_mean,
             ssp.proc_temp_mean, ssp.proc_sal_mean))
logger.debug("std: %s %s %s %s" %
             (ssp.proc_depth_std, ssp.proc_speed_std,
             ssp.proc_temp_std, ssp.proc_sal_std))

# ssp.proc_debug_plot()
# plt.show()

