from datetime import datetime as dt, date, timedelta
from http import client
from urllib import parse
import socket
import logging

from netCDF4 import Dataset

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

url = r"https://opendap.co-ops.nos.noaa.gov/thredds/dodsC/NOAA/GOMOFS/MODELS/201903/nos.gomofs.regulargrid.n003.20190327.t00z.nc"

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
