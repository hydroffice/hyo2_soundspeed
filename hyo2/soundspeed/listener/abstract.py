import logging
import time
import socket
import struct
from threading import Thread, Event

logger = logging.getLogger(__name__)


class AbstractListener(Thread):
    """Common abstract listener"""

    def __init__(self, port=4001, ip="0.0.0.0", timeout=1, datagrams=None, target=None, name="Abstract"):
        Thread.__init__(self, target=target, name=name)
        self.name = self.__class__.__name__
        self.desc = "Abstract listener"  # a human-readable description
        self.ip = ip
        self.port = port
        self.is_multicast = False
        self.timeout = timeout
        self.datagrams = datagrams
        if not self.datagrams:
            self.datagrams = list()

        self.shutdown = Event()

        self.sock_in = None
        self.data = None
        self.sender = None

        # storing raw data
        self._store_disk = False
        self.raw_file = None
        self._store_memory = False
        self.raw_memory = list()

    def start_raw_to_disk(self, filename):
        if self.raw_file:
            self.stop_raw_to_disk()
        self._store_disk = True
        self.raw_file = open(filename, "wb")
        return

    def stop_raw_to_disk(self):
        if self.raw_file:
            self.raw_file.close()
            self._store_disk = False
            self.raw_file = None
        return

    def start_raw_to_memory(self):
        self.stop_raw_to_memory()
        self._store_memory = True

    def stop_raw_to_memory(self):
        self.raw_memory = list()
        self._store_memory = False

    def init_sockets(self):
        self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_in.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_in.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2 ** 16)

        if self.timeout > 0:
            self.sock_in.settimeout(self.timeout)

        self.is_multicast = self.ip[:4] in ["224.", "225."]
        if self.is_multicast:
            # Tell the operating system to add the socket to
            # the multicast group on all interfaces.
            group = socket.inet_aton(self.ip)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.sock_in.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            self.sock_in.bind(('', self.port))

        else:

            try:
                self.sock_in.bind((self.ip, self.port))

            except socket.error as e:
                self.sock_in.close()
                logger.warning("port %d already bound? Not listening anymore. Error: %s"
                               % (self.port, e))
                return False

        return True

    def stop(self):
        """Stop the process"""
        self.shutdown.set()

    def run(self):
        """Start the simulation"""

        # logger.debug("%s start" % self.name)
        if not self.init_sockets():
            return

        count = 0
        while True:
            if self.shutdown.is_set():
                # logger.debug("shutdown")
                break
            # if (count % 20) == 0:
            #     logger.debug("%s: listening" % self.__class__.__name__)
            count += 1

            try:
                self.data, self.sender = self.sock_in.recvfrom(2 ** 16)

            except socket.timeout:
                # logger.info("socket timeout")
                time.sleep(0.1)
                continue

            if self._store_disk:
                self.dump_to_file()
            if self._store_memory:
                self.raw_memory.append(self.data)

            self.parse()

        self.data = None
        self.sender = None
        self.sock_in.close()
        # logger.debug("%s end" % self.name)

    def parse(self):
        raise Exception("Unimplemented function")

    def dump_to_file(self):
        """Default dumper"""
        self.raw_file.write(self.data)

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__
        msg += "  <desc: %s>\n" % self.desc
        return msg
