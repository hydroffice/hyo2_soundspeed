import socket
import time
import logging

from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)


HOST = "localhost"
PORT = 5454
address = (HOST, PORT)
data = "Test data ﻑ"
print(type(data))

# SOCK_DGRAM is UDP, SOCK_STREAM (default) is TCP
# AF_INET (IPv4), AF_INET6 (IPv6)
s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

while True:
    sz = s.sendto(data.encode('utf-8'), address)
    print('%s sent: %s [%s] to %s' % (s.getsockname(), data, sz, address))
    time.sleep(1)
