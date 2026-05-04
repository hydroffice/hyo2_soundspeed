import logging
import socket
from datetime import datetime, timezone, timedelta
from http import client
from urllib import parse

from netCDF4 import Dataset

# noinspection PyUnresolvedReferences
from hyo2.abc2.lib.logging import set_logging
# noinspection PyUnresolvedReferences
from hyo2.abc2.lib.package.pkg_helper import PkgHelper
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.atlas.regofs import RegOfs

set_logging(ns_list=["hyo2.abc2"])

logger = logging.getLogger(__name__)

model = RegOfs.Model.GoMOFS
input_date = datetime.now(timezone.utc)

# download url

url = model.valid_download_url()
if url is None:
    logger.error("no valid file found for today or yesterday")
    exit(-1)
logger.debug("download url: %s", url)

# opendap url

url = model.opendap_url(input_date)
if url is None:
    logger.error("no valid opendap found for today or yesterday")
    exit(-1)
logger.debug("opendap url: %s", url)

# use opendap

file_temp = Dataset(url)
_lat = file_temp.variables["Latitude"][:]
_lon = file_temp.variables["Longitude"][:]

logger.debug("latitude last value: %s", _lat[-1, -1])
logger.debug("longitude last value: %s", _lon[-1, -1])

t = file_temp.variables["temp"][0:1, :][..., 0:1, 0:1]
logger.debug("temperature slice: %s" % (t.shape,))
s = file_temp.variables["salt"][0:1, :][..., 0:1, 0:1]
logger.debug("salinity sclice: %s" % (s.shape,))
