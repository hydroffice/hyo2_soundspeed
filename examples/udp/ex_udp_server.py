# -*- encoding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import socket
import time

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)


def main():

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

if __name__ == "__main__":
    main()
