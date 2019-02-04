import logging
import os
import socket
import struct
import threading
import time
from threading import Lock
from typing import Optional

from hyo2.sis.lib.kng_all import KngAll
from hyo2.sis.lib.kng_kmall import KngKmall

logger = logging.getLogger(__name__)


class ReplayThread(threading.Thread):
    def __init__(self, installation: list, runtime: list, ssp: list, lists_lock: threading.Lock, files: list,
                 replay_timing: float = 1.0, port_in: int = 4001, port_out: int = 26103,
                 ip_out: str = "localhost", target: Optional[object] = None, name: str = "REP",
                 verbose: bool = False, sis_5_mode: bool = False):
        threading.Thread.__init__(self, target=target, name=name)
        self.verbose = verbose
        self.port_in = port_in
        self.port_out = port_out
        self.ip_out = ip_out
        self.sis_5_mode = sis_5_mode
        self.files = files
        self._replay_timing = replay_timing

        self.sock_in = None
        self.sock_out = None

        self.installation = installation
        self.runtime = runtime
        self.ssp = ssp
        self.lists_lock = lists_lock

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

    def _close_sockets(self):
        if self.sock_in:
            self.sock_in.close()
            self.sock_in = None
        if self.sock_out:
            self.sock_out.close()
            self.sock_out = None

    def run(self):
        logger.debug("%s started -> in %s, out %s:%s, timing: %s"
                     % (self.name, self.port_in, self.ip_out, self.port_out, self._replay_timing))

        self.init_sockets()
        while True:
            if self.shutdown.is_set():
                self._close_sockets()
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

        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.sis_5_mode:
            # allow reuse of addresses
            self.sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Messages time-to-live to 1 to avoid forwarding beyond current network segment.
            ttl = struct.pack('b', 1)  # TODO: How does K-Controller control this?
            self.sock_out.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        self.sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2 ** 16)

        logger.debug("sock_out > buffer %sKB" %
                     (self.sock_out.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) / 1024))

    def interaction(self):
        # logger.debug("reading files")

        self.dg_counter = 0

        for fp in self.files:
            if self.shutdown.is_set():
                self._close_sockets()
                break

            fp_ext = os.path.splitext(fp)[-1].lower()
            if self.sis_5_mode:
                if fp_ext not in [".kmall", ".kmwcd"]:
                    logger.info("SIS 5 mode -> skipping unsupported file extension: %s" % fp)
                    continue
            else:
                if fp_ext not in [".all", ".wcd"]:
                    logger.info("SIS 4 mode -> skipping unsupported file extension: %s" % fp)
                    continue

            try:
                f = open(fp, 'rb')
                f_sz = os.path.getsize(fp)

            except (OSError, IOError):
                raise RuntimeError("unable to open %s" % fp)

            logger.debug("open file: %s [%iKB]" % (fp, (f_sz / 1024)))

            while True:

                if self.shutdown.is_set():
                    self._close_sockets()
                    break

                if self.sis_5_mode:
                    break_loop = self._sis_5(f, f_sz)
                else:
                    break_loop = self._sis_4(f, f_sz)
                if break_loop:
                    break

                if f.tell() >= f_sz:
                    # end of file
                    logger.debug("EOF")
                    break

            f.close()
            if self.verbose:
                logger.debug("data loaded > datagrams: %s" % self.dg_counter)

    def _sis_5(self, f, f_sz) -> bool:
        # guardian to avoid to read beyond the EOF
        if (f.tell() + 20) > f_sz:
            if self.verbose:
                logger.debug("EOF")
            return True

        base = KngKmall(verbose=True)
        ret = base.read(f, f_sz)

        if ret == KngKmall.Flags.VALID:

            self.dg_counter += 1

        elif ret == KngKmall.Flags.UNEXPECTED_EOF:

            logger.warning("troubles in reading file > SKIP (reason: unexpected EOF)")
            return True

        elif ret == KngKmall.Flags.CORRUPTED_END_DATAGRAM:

            f.seek(-(base.length + 1), 1)
            logger.warning("troubles in reading final datagram part > REALIGN to position: %s" % f.tell())

        else:
            raise RuntimeError("unknown return %s from KngKmall" % ret)

        # Read and send only the desired datagrams:
        # b'#IIP': 'Installation parameters and sensor setup'
        # b'#IOP': 'Runtime parameters as chosen by operator'
        # b'#IBE': 'Built in test (BIST) error report'
        # b'#IBR': 'Built in test (BIST) reply'
        # b'#IBS': 'Built in test (BIST) short reply'
        #
        # b'#MRZ': 'Multibeam (M) raw range (R) and depth(Z) datagram'
        # b'#MWC': 'Multibeam (M) water (W) column (C) datagram'
        #
        # b'#SPO': 'Sensor (S) data for position (PO)'
        # b'#SKM': 'Sensor (S) KM binary sensor format'
        # b'#SVP': 'Sensor (S) data from sound velocity (V) profile (P) or CTD'
        # b'#SVT': 'Sensor (S) data for sound velocity (V) at transducer (T)'
        # b'#SCL': 'Sensor (S) data from clock (CL)'
        # b'#SDE': 'Sensor (S) data from depth (DE) sensor'
        # b'#SHI': 'Sensor (S) data for height (HI)'
        #
        # b'#CPO': 'Compatibility (C) data for position (PO)'
        # b'#CHE': 'Compatibility (C) data for heave (HE)'
        if base.type in [b'#IIP', b'#IOP', b'#MRZ', b'#MWC', b'#SPO', b'#SVP', b'#SVT',
                         b'#CPO', b'#CHE']:
            logger.debug("%s > sending dg %s (length: %sB)"
                         % (base.datetime.strftime('%Y-%m-%d %H:%M:%S.%f'), base.type, base.length))
            f.seek(-base.length, 1)
            dg_data = f.read(base.length)

            # Stores a few datagrams of interest in data lists:
            with self.lists_lock:
                if base.type == b'#IIP':
                    self.installation.append(dg_data)
                if base.type == b'#IOP':
                    self.runtime.append(dg_data)
                if base.type == b'#SVP':
                    self.ssp.append(dg_data)

            self.sock_out.sendto(dg_data, (self.ip_out, self.port_out))

            with self._lock:
                time.sleep(self._replay_timing)

        return False

    def _sis_4(self, f, f_sz) -> bool:
        # guardian to avoid to read beyond the EOF
        if (f.tell() + 16) > f_sz:
            if self.verbose:
                logger.debug("EOF")
            return True

        base = KngAll(verbose=True)
        ret = base.read(f, f_sz)
        if ret == KngAll.Flags.MISSING_FIRST_STX:

            if self.verbose:
                logger.warning("troubles in reading file > SKIP")
            return True

        elif ret == KngAll.Flags.CORRUPTED_START_DATAGRAM:

            f.seek(-15, 1)  # +1 byte from initial header position
            logger.warning("troubles in reading initial datagram part > REALIGN to position: %s" % f.tell())
            return False

        elif ret == KngAll.Flags.UNEXPECTED_EOF:

            logger.warning("troubles in reading file > SKIP (reason: unexpected EOF)")
            return True

        elif ret == KngAll.Flags.CORRUPTED_END_DATAGRAM:

            f.seek(-(base.length + 3), 1)
            logger.warning("troubles in reading final datagram part > REALIGN to position: %s" % f.tell())

        elif ret == KngAll.Flags.VALID:

            self.dg_counter += 1

        else:
            raise RuntimeError("unknown return %s from KngAll" % ret)

        # Read and send only the desired datagrams:
        # - position (0x50)
        # - XYZ88 (0x58)
        # - sound speed profile (0x55)
        # - runtime parameters (0x52)
        # - installation parameters (0x49)
        # - range/angle (0x4e) for coverage modeling.
        # - seabed imagery (0x59)
        # - watercolumn (0x6b)
        if base.id in [0x4e, 0x49, 0x50, 0x52, 0x55, 0x58, 0x59, 0x6b]:
            logger.debug("%s %s > sending dg #%s(%s) (length: %sB)"
                         % (base.date, base.time, hex(base.id), base.id, base.length))
            f.seek(-base.length, 1)
            dg_data = f.read(base.length)

            # Stores a few datagrams of interest in data lists:
            with self.lists_lock:
                if base.id == 0x49:
                    self.installation.append(dg_data)
                if base.id == 0x52:
                    self.runtime.append(dg_data)
                if base.id == 0x55:
                    self.ssp.append(dg_data)

            self.sock_out.sendto(dg_data, (self.ip_out, self.port_out))

            with self._lock:
                time.sleep(self._replay_timing)

        return False
