import logging

from hyo2.soundspeed.profile.oceanography import Oceanography as Oc
from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)

# check values from Fofonoff and Millard(1983)
trusted_fof_d = 9712.653  # m
trusted_fof_p = 10000  # dBar
trusted_fof_lat = 30.0

# check values from generate_gsw_trusted_values
trusted_gsw_d = 9713.7  # m
trusted_gsw_p = 10000  # dBar
trusted_gsw_lat = 30.0

calc_d = Oc.p2d_backup(p=trusted_fof_p, lat=trusted_fof_lat)
logger.info("Backup: Depth: %.3f <> %.3f" % (calc_d, trusted_fof_d))

calc_d = Oc.p2d_gsw(p=trusted_gsw_p, lat=trusted_gsw_lat, dyn_height=None)
logger.info("GSW: Depth: %.3f <> %.3f" % (calc_d, trusted_gsw_d))

calc_p = Oc.d2p_backup(d=calc_d, lat=trusted_fof_lat)
logger.info("Backup: Pressure: %.3f <> %.3f" % (calc_p, trusted_fof_p))

calc_p = Oc.d2p_gsw(d=trusted_gsw_d, lat=trusted_gsw_lat, dyn_height=None)
logger.info("GSW: Pressure: %.3f <> %.3f" % (calc_p, trusted_gsw_p))
