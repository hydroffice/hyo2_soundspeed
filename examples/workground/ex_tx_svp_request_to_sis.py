import functools
import logging
import operator
import socket

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

sis_svp_ip = '127.0.0.1'
sis_svp_port = 4001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# We try all of them in the hopes that one works.
sensors = ["710", "122", "302", "3020", "2040"]
for idx, sensor in enumerate(sensors):
    # talker ID, Roger Davis (HMRG) suggested SM based on something KM told him
    smr20_message = '$SMR20,EMX=%s,' % sensor

    # calculate checksum, XOR of all bytes after the $
    checksum = functools.reduce(operator.xor, map(ord, smr20_message[1:len(smr20_message)]))

    # append the checksum and end of datagram identifier
    smr20_message += "*{0:02x}".format(checksum)
    smr20_message += "\\\r\n"

    logger.debug("SMR20 datagram:\n%s" % smr20_message)

    sock.sendto(smr20_message.encode(), (sis_svp_ip, sis_svp_port))
    logger.debug("SMR20 datagram sent")

sock.close()
