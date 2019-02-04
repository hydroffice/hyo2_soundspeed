import socket
import struct
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)


multicast_group = '224.1.20.40'
server_address = ('', 6020)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(server_address)

# Tell the operating system to add the socket to
# the multicast group on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Receive/respond loop
while True:

    logger.debug('waiting to receive message ...')
    data, address = sock.recvfrom(2 ** 16)  # 2**15 is max UDP datagram size

    logger.debug('received %d bytes from %s' % (len(data), address))
    logger.debug('received data: %s' % data)

