import logging
import time
import socket
import struct
from threading import Thread, Event
from typing import Optional

logger = logging.getLogger(__name__)


class AbstractListener(Thread):
    """Common abstract listener"""

    def __init__(self, port: int = 4001, ip: str = "0.0.0.0", timeout: int = 1,
                 datagrams: Optional[list] = None,
                 target: Optional[object] = None, name: Optional[str] = "Abstract",
                 debug: bool = False) -> None:
        Thread.__init__(self, target=target, name=name)
        self.name = self.__class__.__name__
        self.desc = "Abstract listener"  # a human-readable description
        self.ip = ip
        self.port = port
        self.is_multicast = False  # True for K-Ctrl
        self.timeout = timeout
        self.datagrams = datagrams
        if not self.datagrams:
            self.datagrams = list()
        self.debug = debug

        self.shutdown = Event()
        self.sock_in = None
        self.data = None
        self.sender = None

    def init_sockets(self) -> bool:
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
                if self.debug:
                    logger.debug('%s bound to %s@%s' % (self.desc, self.ip, self.port))

            except socket.error as e:
                self.sock_in.close()
                logger.warning("port %d already bound? Not listening anymore. Error: %s"
                               % (self.port, e))
                return False

        return True

    def stop(self) -> None:
        """Stop the process"""
        self.shutdown.set()

    def run(self) -> None:
        """Start the simulation"""

        # logger.debug("%s start" % self.name)
        if not self.init_sockets():
            return

        count = 0
        while True:
            if self.shutdown.is_set():
                if self.debug:
                    logger.info("shutdown")
                break
            # if (count % 20) == 0:
            #     logger.debug("%s: listening" % self.__class__.__name__)
            count += 1

            try:
                self.data, self.sender = self.sock_in.recvfrom(2 ** 16)

            except socket.timeout:
                if self.debug:
                    logger.info("socket timeout")
                time.sleep(0.1)
                continue

            self.parse()

        self.data = None
        self.sender = None
        self.sock_in.close()
        # logger.debug("%s end" % self.name)

    def parse(self) -> None:
        raise Exception("Unimplemented function")

    def __repr__(self) -> str:
        msg = "<%s>\n" % self.__class__.__name__
        msg += "  <desc: %s>\n" % self.desc
        msg += "  <ip: %s>\n" % self.ip
        msg += "  <port: %s>\n" % self.port
        msg += "  <multicast: %s>\n" % self.is_multicast
        return msg
