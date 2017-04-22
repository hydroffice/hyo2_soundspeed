import os

from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeed.profile.oceanography import Oceanography as Oc

# check values from Fofonoff and Millard(1983)
atg_ck = 3.255976e-4
s_ck = 40.0
t_ck = 40
p_ck = 10000
atg_calc = Oc.atg(s=s_ck, t=t_ck, p=p_ck)
logger.info("Adiabatic Temperature Gradient: %g <> %g" % (atg_calc, atg_ck))

theta_ck = 36.89073
s_ck = 40
t0_ck = 40
p0_ck = 10000
p_ref_ck = 0
theta_calc = Oc.pot_temp(s=s_ck, t=t0_ck, p=p0_ck, pr=p_ref_ck)
logger.info("Theta: %g <> %g" % (theta_calc, theta_ck))
t0_calc = Oc.in_situ_temp(s=s_ck, t=theta_ck, p=p0_ck, pr=p_ref_ck)
logger.info("Temp: %.3f <> %.3f" % (t0_calc, t0_ck))

cr_ck = 1.1
t_ck = 40.0
s_ck = 38.999
s_calc = Oc.cr2s(cr=cr_ck, t=t_ck)
logger.info("Sal: %.3f <> %.3f" % (s_calc, s_ck))

c_ck = 75
t_ck = 40
p_ck = 10000
s_ck = 36.616
s_calc = Oc.c2s(c=c_ck, t=t_ck, p=p_ck)
logger.info("Sal: %.3f <> %.3f" % (s_calc, s_ck))
c_calc = Oc.s2c(s=s_calc, p=p_ck, t=t_ck)
logger.info("Cond: %.3f <> %.3f" % (c_calc, c_ck))
