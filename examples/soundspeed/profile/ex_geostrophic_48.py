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

# gold ref using the matlab script: generate_gsw_trusted_values.m and GSW 3.05

# - @ 1000m

# absolute salinity
sa = np.array([34.7118, 34.8915, 35.0256, 34.8472, 34.7366, 34.7324])
# conservative temperature
ct = np.array([28.8099, 28.4392, 22.7862, 10.2262,  6.8272,  4.3236])
# sea pressure
p = np.array([10.0, 50.0, 125.0, 250.0, 600.0, 1000.0])
p_ref = 1000.0
# golden reference values
gold_ref = np.array([17.0392, 14.6659, 10.9129, 7.5679, 3.3935, 0])

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
gold_ref = np.array([12.5588, 10.1854, 6.4324, 3.0875, -1.0869, -4.4804])

calc_out = geostrophic_48.geo_strf_dyn_height(SA=sa, CT=ct, p=p, p_ref=p_ref)
print("\n@500")
print("gold: %s" % gold_ref)
print("calc: %s" % calc_out)
print("diff: %s" % (calc_out - gold_ref))

# - @ 0m

# absolute salinity
sa = np.array([34.7118, 34.8915, 35.0256, 34.8472, 34.7366, 34.7324])
# conservative temperature
ct = np.array([28.8099, 28.4392, 22.7862, 10.2262,  6.8272,  4.3236])
# sea pressure
p = np.array([10.0, 50.0, 125.0, 250.0, 600.0, 1000.0])
p_ref = 0.0
# golden reference values
gold_ref = np.array([-0.6008, -2.9742, -6.7272, -10.0721, -14.2465, -17.6400])

calc_out = geostrophic_48.geo_strf_dyn_height(SA=sa, CT=ct, p=p, p_ref=p_ref)
print("\n@0")
print("gold: %s" % gold_ref)
print("calc: %s" % calc_out)
print("diff: %s" % (calc_out - gold_ref))
