import logging
from enum import Enum
import socket

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)-9s > %(message)s")
logger = logging.getLogger(__name__)


class KSSIS(Enum):

    DETECTION_OF_SOUNDERS = 0,
    REQUEST_CURRENT_SVP = 1,
    START_PINGING = 2,
    STOP_PINGING = 3,
    TERMINATE = 99


kssis_type = KSSIS.REQUEST_CURRENT_SVP

kctrl_ip = '127.0.0.1'
kctrl_port = 14002
ssm_port = 4002

sounder_name = "EM124_101"

if kssis_type == KSSIS.DETECTION_OF_SOUNDERS:

    kssis_msg = '$KSSIS,997'

elif kssis_type == KSSIS.REQUEST_CURRENT_SVP:

    kssis_msg = '$KSSIS,454,%s' % sounder_name

elif kssis_type == KSSIS.START_PINGING:

    kssis_msg = '$KSSIS,458,%s' % sounder_name

elif kssis_type == KSSIS.STOP_PINGING:

    kssis_msg = '$KSSIS,457,%s' % sounder_name

elif kssis_type == KSSIS.TERMINATE:

    kssis_msg = '$KSSIS,24'

else:
    raise RuntimeError("invalid message type: %s" % kssis_type)

logger.debug("S01 datagram:\n%s" % kssis_msg)

rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
rx_sock.bind(('127.0.0.1', ssm_port))

tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tx_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

tx_sock.sendto(kssis_msg.encode(), (kctrl_ip, kctrl_port))
tx_sock.close()
logger.debug("tx: %s" % kssis_msg)

# Receive/respond loop
while True:

    # logger.debug('waiting to receive message ...')
    data, address = rx_sock.recvfrom(2 ** 16)  # 2**15 is max UDP datagram size

    # if kmall_verbose:
    # logger.debug('received %d bytes from %s' % (len(data), address))
    logger.debug('rx: %s' % data)
    tokens = data.split(b',')
    if len(tokens) < 2:
        continue
    # if tokens[1] == b'12':
    #     logger.debug('received data: %s' % data)
