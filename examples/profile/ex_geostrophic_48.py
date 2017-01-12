import os
import numpy as np
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hydroffice.soundspeed.profile import geostrophic_48

# data source: http://www.teos-10.org/pubs/gsw/html/gsw_geo_strf_dyn_height.html

# - @ 1000m

# absolute salinity
sa = np.array([34.7118, 34.8915, 35.0256, 34.8472, 34.7366, 34.7324])
# conservative temperature
ct = np.array([28.8099, 28.4392, 22.7862, 10.2262,  6.8272,  4.3236])
# sea pressure
p = np.array([10.0, 50.0, 125.0, 250.0, 600.0, 1000.0])
p_ref = 1000.0
# golden reference values
gold_ref = np.array([17.039204557769487, 14.665853784722286, 10.912861136923812, 7.567928838774945, 3.393524055565328, 0])

calc_out = geostrophic_48.geo_strf_dyn_height(SA=sa, CT=ct, p=p, p_ref=p_ref)
print("@1000")
print("gold: %s" % gold_ref)
print("calc: %s" % calc_out)
print("diff: %s" % (calc_out - gold_ref))

# - @ 500m

# absolute salinity
sa = np.array([34.7118, 34.8915, 35.0256, 34.8472, 34.7366, 34.7324])
# conservative temperature
ct = np.array([28.8099, 28.4392, 22.7862, 10.2262,  6.8272,  4.3236])
# sea pressure
p = np.array([10.0, 50.0, 125.0, 250.0, 600.0, 1000.0])
p_ref = 500.0
# golden reference values
gold_ref = np.array([12.591685524603520, 10.232579492691912, 6.487295712474179, 3.200564075666534, -1.093343750292661, -4.700552560409960])

calc_out = geostrophic_48.geo_strf_dyn_height(SA=sa, CT=ct, p=p, p_ref=p_ref)
print("\n@500")
print("gold: %s" % gold_ref)
print("calc: %s" % calc_out)
print("diff: %s" % (calc_out - gold_ref))
