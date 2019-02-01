import socket
import struct
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)


multicast_group = '225.1.20.40'
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

    # Using Dictionary for now until I learn to write the kmallbase class
    hdr_Bytes = struct.unpack('<I4sBBHII', data[0:20])

    hdr_data = dict()
    hdr_data['length'] = hdr_Bytes[0]
    hdr_data['dg_id'] = hdr_Bytes[1]
    hdr_data['dg_Ver'] = hdr_Bytes[2]
    hdr_data['sys_id'] = hdr_Bytes[3]
    hdr_data['model'] = hdr_Bytes[4]
    hdr_data['time_sec'] = hdr_Bytes[5]
    hdr_data['time_nsec'] = hdr_Bytes[6]

    # Print to debug the datagram id
    logger.debug('DatagramID: %s' % hdr_Bytes[1])

    # If hdr_data['dg_id'] == #SVP continue parsing
    if hdr_data['dg_id'].decode() == '#SVP':
        logger.debug('This is an SVP DATAGRAM Hooray!!!!!!')

    sock.sendto(b'ack', address)
    logger.debug('sent ack to %s' % (address, ))
