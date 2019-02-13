from datetime import datetime, timedelta
import socket
import struct
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)


kmall_mode = True
kmall_verbose = False

kmall_datagrams = {
    b'#IIP': 'Installation parameters and sensor setup',
    b'#IOP': 'Runtime parameters as chosen by operator',
    b'#IBE': 'Built in test (BIST) error report',
    b'#IBR': 'Built in test (BIST) reply',
    b'#IBS': 'Built in test (BIST) short reply',

    b'#MRZ': 'Multibeam (M) raw range (R) and depth(Z) datagram',
    b'#MWC': 'Multibeam (M) water (W) column (C) datagram',

    b'#SPO': 'Sensor (S) data for position (PO)',
    b'#SKM': 'Sensor (S) KM binary sensor format',
    b'#SVP': 'Sensor (S) data from sound velocity (V) profile (P) or CTD',
    b'#SVT': 'Sensor (S) data for sound velocity (V) at transducer (T)',
    b'#SCL': 'Sensor (S) data from clock (CL)',
    b'#SDE': 'Sensor (S) data from depth (DE) sensor',
    b'#SHI': 'Sensor (S) data for height (HI)',

    b'#CPO': 'Compatibility (C) data for position (PO)',
    b'#CHE': 'Compatibility (C) data for heave (HE)',
}

kmall_filter = [b'#SVP']  # kmall_datagrams.keys()

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

logger.debug("multicast settings: %s:%s" % (multicast_group, server_address[1]))

# Receive/respond loop
while True:

    logger.debug('waiting to receive message ...')
    data, address = sock.recvfrom(2 ** 16)  # 2**15 is max UDP datagram size

    # if kmall_verbose:
    logger.debug('received %d bytes from %s' % (len(data), address))
    logger.debug('received data: %s' % data)

    if not kmall_mode:
        sock.sendto(b'ack', address)
        logger.debug('sent ack to %s' % (address,))
        continue

    # parsing assuming KMALL format

    dgm_size = struct.unpack("<I", data[:4])
    if kmall_verbose:
        logger.debug('size: %s' % dgm_size)
    dgm_type_as_bytes_list = struct.unpack("<cccc", data[4:8])
    dgm_type = b''.join(dgm_type_as_bytes_list)

    if dgm_type not in kmall_filter:
        continue

    try:
        logger.debug('type: %s -> %s' % (dgm_type, kmall_datagrams[dgm_type]))
    except KeyError as e:
        logger.debug("invalid Kmall datagram type: %s" % e)
        break

    if kmall_verbose:
        dgm_version = struct.unpack("<B", data[8:9])
        logger.debug('version: %s' % dgm_version)
        dgm_system_id = struct.unpack("<B", data[9:10])
        logger.debug('system id: %s' % dgm_system_id)
        dgm_sounder_id = struct.unpack("<H", data[10:12])
        logger.debug('sounder id: %s' % dgm_sounder_id)
        dgm_time_sec = struct.unpack("<I", data[12:16])[0]
        logger.debug('time sec: %s' % dgm_time_sec)
        dgm_time_nanosec = struct.unpack("<I", data[16:20])[0]
        logger.debug('time nanosec: %s' % dgm_time_nanosec)
        dgm_datetime = datetime.utcfromtimestamp(dgm_time_sec) + \
                       timedelta(microseconds=(dgm_time_nanosec / 1000.0))
        logger.debug('datetime: %s' % dgm_datetime.strftime('%Y-%m-%d %H:%M:%S.%f'))
