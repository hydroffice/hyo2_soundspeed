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

    print("default timeout: %s" % socket.getdefaulttimeout())  # initial value is None

    HOST = "localhost"
    PORT = 5454

    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    try:
        s.bind((HOST, PORT))
    except socket.error as e:
        exit("unable to bind to: %s:%s" % (HOST, PORT))
    print("socket: %s %s" % s.getsockname())

    while True:
        data, address = s.recvfrom(4096)
        data = data.decode('utf-8')
        print("rx: %s [%s] from %s" % (data, len(data), address))

if __name__ == "__main__":
    main()
