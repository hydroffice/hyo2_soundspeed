from http import client
from urllib import parse
import socket
import logging
from netCDF4 import Dataset

from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.ssm2.app.gui.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)

url = r"https://prod.opendap.co-ops.nos.noaa.gov/thredds/dodsC/NOAA/GOMOFS/MODELS/2020/06/01/nos.gomofs.regulargrid.n003.20200601.t00z.nc"

try:
    p = parse.urlparse(url)
    conn = client.HTTPSConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    conn.close()
    logger.debug("passed url: %s -> %s" % (url, resp.status))

except socket.error as e:
    logger.warning("while checking %s, %s" % (url, e))
    exit(-1)

file_temp = Dataset(url)
_lat = file_temp.variables['Latitude'][:]
_lon = file_temp.variables['Longitude'][:]

logger.debug("latitude: %s" % _lat[-1, -1])
logger.debug("longitude: %s" % _lon[-1, -1])

t = file_temp.variables['temp'][0:1, :][..., 0:1, 0:1]
logger.debug(t.shape)
s = file_temp.variables['salt'][0:1, :][..., 0:1, 0:1]
