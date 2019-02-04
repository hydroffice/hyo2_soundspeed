from datetime import datetime, timedelta
import socket
import struct
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)


kongsberg_mode = True

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

    logger.debug('\nwaiting to receive message ...')
    data, address = sock.recvfrom(2 ** 16)  # 2**15 is max UDP datagram size

    logger.debug('received %d bytes from %s' % (len(data), address))
    logger.debug('received data: %s' % data)

    if not kongsberg_mode:
        sock.sendto(b'ack', address)
        logger.debug('sent ack to %s' % (address,))
        continue

    dgm_size = struct.unpack("<I", data[:4])
    logger.debug('size: %s' % dgm_size)
    dgm_type_as_bytes_list = struct.unpack("<cccc", data[4:8])
    dgm_type = b''.join(dgm_type_as_bytes_list)
    logger.debug('type: %s' % (dgm_type, ))
    dgm_version = struct.unpack("<B", data[8:9])
    logger.debug('version: %s' % dgm_version)
    dgm_system_id = struct.unpack("<B", data[9:10])
    logger.debug('system id: %s' % dgm_system_id)
    dgm_sounder_id = struct.unpack("<H", data[10:12])
    logger.debug('sounder id: %s' % dgm_sounder_id)

    dgm_time_sec = struct.unpack("<I", data[12:16])[0]
    logger.debug('time sec: %s' % dgm_time_sec)
    dgm_time_microsec = struct.unpack("<I", data[16:20])[0] * 10e-3
    logger.debug('time microsec: %s' % dgm_time_microsec)
    dgm_datetime = datetime.utcfromtimestamp(dgm_time_sec) + timedelta(microseconds=dgm_time_microsec)
    logger.debug('datetime: %s' % dgm_datetime.strftime('%Y-%m-%d %H:%M:%S.%f'))

