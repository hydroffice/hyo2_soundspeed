# logging settings
import logging
import os
import socket
import threading
import time
from threading import Lock

logger = logging.getLogger(__name__)

from hyo2.sis.lib.kmbase import KmBase


class ReplayThread(threading.Thread):
    def __init__(self,
                 installation,
                 runtime,
                 ssp,
                 files,
                 replay_timing=1.0,
                 port_in=4001,
                 port_out=26103,
                 ip_out="localhost",
                 target=None,
                 name="SVP",
                 verbose=False):
        threading.Thread.__init__(self, target=target, name=name)
        self.verbose = verbose
        self.port_in = port_in
        self.port_out = port_out
        self.ip_out = ip_out
        self.files = files
        self._replay_timing = replay_timing
        logger.debug("input port: %s" % self.port_in)
        logger.debug("output port: %s" % self.port_out)
        logger.debug("output address: %s" % self.ip_out)
        logger.debug("reply timing: %s" % self._replay_timing)

        self.sock_in = None
        self.sock_out = None

        self.installation = installation
        self.runtime = runtime
        self.ssp = ssp

        self.dg_counter = None

        self.shutdown = threading.Event()
        self._lock = Lock()
        self._external_lock = False

    @property
    def replay_timing(self):
        if not self._external_lock:
            raise RuntimeError("Accessing resources without locking them!")
        return self._replay_timing

    @replay_timing.setter
    def replay_timing(self, value):
        if not self._external_lock:
            raise RuntimeError("Modifying resources without locking them!")
        self._replay_timing = value

    def lock_data(self):
        self._lock.acquire()
        self._external_lock = True

    def unlock_data(self):
        self._lock.release()
        self._external_lock = False

    def run(self):
        if self.verbose:
            logger.debug("%s started" % self.name)

        self.init_sockets()
        while True:
            if self.shutdown.is_set():
                break
            self.interaction()
            time.sleep(1)
            logger.debug("sleep")

        logger.debug("%s ended" % self.name)

    def stop(self):
        """Stop the thread"""
        self.shutdown.set()

    def init_sockets(self):
        """Initialize UDP sockets"""

        # self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock_in.settimeout(1)
        # self.sock_in.bind(("0.0.0.0", self.port_in))

        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2 ** 16)

        logger.debug("sock_out > buffer %sKB" %
                     (self.sock_out.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) / 1024))

    def interaction(self):
        # logger.debug("reading files")

        self.dg_counter = 0

        for fp in self.files:
            if self.shutdown.is_set():
                break

            try:
                f = open(fp, 'rb')
                f_sz = os.path.getsize(fp)

            except (OSError, IOError):
                raise RuntimeError("unable to open %s" % fp)

            logger.debug("open file: %s [%iKB]" % (fp, (f_sz / 1024)))

            while True:

                if self.shutdown.is_set():
                    break

                # guardian to avoid to read beyond the EOF
                if (f.tell() + 16) > f_sz:
                    if self.verbose:
                        logger.debug("EOF")
                    break

                base = KmBase(verbose=True)
                ret = base.read(f, f_sz)
                if ret == base.flags["MISSING_FIRST_STX"]:

                    if self.verbose:
                        logger.debug("troubles in reading file > SKIP")
                    break

                elif ret == base.flags["CORRUPTED_START_DATAGRAM"]:

                    f.seek(-15, 1)  # +1 byte from initial header position
                    logger.debug("troubles in reading initial datagram part > REALIGN to position: %s" % f.tell())
                    continue

                elif ret == base.flags["UNEXPECTED_EOF"]:

                    logger.debug("troubles in reading file > SKIP (reason: unexpected EOF)")
                    break

                elif ret == base.flags["CORRUPTED_START_DATAGRAM"]:

                    f.seek(-(base.length + 3), 1)
                    logger.debug("troubles in reading final datagram part > REALIGN to position: %s" % f.tell())

                elif ret == base.flags["VALID"]:

                    self.dg_counter += 1

                else:
                    raise RuntimeError("unknown return %s from Kongsberg base" % ret)

                # Read and send only the desired datagrams:
                # - position (0x50)
                # - XYZ88 (0x58)
                # - sound speed profile (0x55)
                # - runtime parameters (0x52)
                # - installation parameters (0x49)
                # - range/angle (0x4e) for coverage modeling.
                # - seabed imagery (0x59)
                # - watercolumn (0x6b)
                if (base.id == 0x4e) or (base.id == 0x49) or (base.id == 0x50) or (base.id == 0x52) or \
                        (base.id == 0x55) or (base.id == 0x58) or (base.id == 0x59) or (base.id == 0x6b):
                    logger.debug("%s %s > sending dg #%s (length: %sB)"
                                 % (base.date, base.time, base.id, base.length))
                    f.seek(-base.length, 1)
                    dg_data = f.read(base.length)

                    # If we come across a runtime datagram then set it in the bounce back thread
                    if id == 0x49:
                        self.installation.append(dg_data)

                    # If we come across a runtime datagram then set it in the bounce back thread
                    if id == 0x52:
                        self.runtime.append(dg_data)

                    # If we come across an SVP datagram then set it in the bounce back thread
                    if id == 0x55:
                        self.ssp.append(dg_data)

                    self.sock_out.sendto(dg_data, (self.ip_out, self.port_out))

                    self._lock.acquire()
                    time.sleep(self._replay_timing)
                    self._lock.release()

                if f.tell() >= f_sz:
                    # end of file
                    logger.debug("EOF")
                    break

            f.close()
            if self.verbose:
                logger.debug("data loaded > datagrams: %s" % self.dg_counter)
