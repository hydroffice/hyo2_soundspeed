import logging

import numpy as np
from matplotlib import pyplot as plt

from hyo2.abc2.lib.logging import set_logging
from hyo2.ssm2.lib.profile.profile import Profile

set_logging(ns_list=["hyo2.abc2", "hyo2.ssm2"])

logger = logging.getLogger(__name__)


def fresh_profile():
    ssp = Profile()
    d = np.arange(0.0, 100.0, 0.5)
    vs = np.arange(500.0, 1500.0, 5.0)
    t = np.arange(0.0, 100.0, 0.5)
    s = np.arange(0.0, 100.0, 0.5)
    ssp.init_proc(d.size)
    ssp.proc.depth = d
    ssp.proc.speed = vs
    ssp.proc.temp = t
    ssp.proc.sal = s
    # ssp.proc.flag[40:50] = 1
    # ssp.proc.flag[50:70] = 2
    return ssp


# ssp = fresh_profile()
# d_mid = 30.0
# vs_mid = 1450.0
# ssp.insert_proc_speed(depth=d_mid, speed=vs_mid)
# d_mid = 31.0
# vs_mid = 1455.0
# ssp.insert_proc_speed(depth=d_mid, speed=vs_mid)
# ssp.proc_debug_plot()
# plt.show()

ssp = fresh_profile()
d_mid = -1.0
vs_mid = 1400.0
ssp.insert_proc_speed(depth=d_mid, speed=vs_mid)
ssp.proc_debug_plot()
plt.show()
