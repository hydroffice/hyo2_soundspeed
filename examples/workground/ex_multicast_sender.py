import socket
import struct
import logging
import time

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)


message = b'test data'
multicast_group = ('225.1.20.40', 6020)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set a timeout to avoid socket blocking while waiting
sock.settimeout(3)

# Messages time-to-live to 1 to avoid forwarding beyond current network segment.
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

# Look for responses from all recipients
while True:

    logger.debug('sending %s' % message)
    sent = sock.sendto(message, multicast_group)

    logger.debug('waiting to receive ...')
    try:
        data, server = sock.recvfrom(2 ** 16)  # 2**15 is max UDP datagram size
    except socket.timeout:
        logger.info('timed out -> no more responses')
        break
    logger.debug('received %s from %s' % (data, server))

    time.sleep(3)  # to reduce transmission rate

logger.debug('closing socket')
sock.close()
