import functools
import logging
import operator
import socket
from datetime import datetime

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

sis_svp_ip = '127.0.0.1'
sis_svp_port = 4001

# a short profile
depths = [0.00, 2.60, 24.60, 81.80, 203.60, 500.00, 1000.00, 2000.00, 4000.00, 12000.00]
speeds = [1539.5, 1543.2, 1543.4, 1535.5, 1526.0, 1494.6, 1483.0, 1492.6, 1525.3, 1675.8]
temps = [27.29, 28.94, 28.84, 24.67, 20.15, 9.18, 4.11, 2.35, 1.84, 2.46]
sals = [34.85, 34.84, 34.86, 35.51, 35.64, 34.62, 34.49, 34.64, 34.72, 34.70]

# initial section
s01_message = '$MVS01,00000,%04d,%s' % (len(depths), datetime.utcnow().strftime("%H%M%S,%d,%m,%Y,"))

# samples section
for i in range(len(depths)):
    s01_message += "%.2f,%1f,%.2f,%.2f,\r\n" % (depths[i], speeds[i], temps[i], sals[i])

# lat and lon section
lat_deg = 10
lat_min = 20
lat_decimal_min = 30
lat_hem = 'N'
lat_str = '%02d%02d.%02d,%s,' % (lat_deg, lat_min, lat_decimal_min, lat_hem)
lon_deg = 30
lon_min = 20
lon_decimal_min = 10
lon_hem = 'W'
lon_str = '%02d%02d.%02d,%s,' % (lon_deg, lon_min, lon_decimal_min, lon_hem)
s01_message += lat_str + lon_str + "0.0,test comment,"

# calculate checksum, XOR of all bytes after the $
checksum = functools.reduce(operator.xor, map(ord, s01_message[1:]))
s01_message += "*%02x" % checksum
s01_message += "\\\r\n"

logger.debug("S01 datagram:\n%s" % s01_message)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.sendto(s01_message.encode(), (sis_svp_ip, sis_svp_port))
sock.close()
logger.debug("S01 datagram sent")