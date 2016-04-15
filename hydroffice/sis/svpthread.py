# -*- encoding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import time
import threading
import socket
import struct
import numpy as np

# logging settings
import logging
logger = logging.getLogger(__name__)


class SvpThread(threading.Thread):
    def __init__(self, installation, runtime, ssp,
                 port_in=4001, port_out=26103, ip_out="localhost",
                 target=None, name="SVP", verbose=None):
        threading.Thread.__init__(self, target=target, name=name)
        self.port_in = port_in
        self.port_out = port_out
        self.ip_out = ip_out
        logger.debug("input port: %s" % self.port_in)
        logger.debug("output port: %s" % self.port_out)
        logger.debug("output address: %s" % self.ip_out)

        self.sock_in = None
        self.sock_out = None

        self.installation = installation
        self.runtime = runtime
        self.ssp = ssp

        self.shutdown = threading.Event()

    def run(self):
        logger.debug("%s start" % self.name)
        self.init_sockets()
        while True:
            if self.shutdown.is_set():
                break
            self.interaction()
            time.sleep(1)
        logger.debug("%s end" % self.name)

    def stop(self):
        """Stop the thread"""
        self.shutdown.set()

    def init_sockets(self):
        """Initialize UDP sockets"""

        self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_in.settimeout(10)
        self.sock_in.bind(("0.0.0.0", self.port_in))

        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2 ** 16)
        logger.debug("sock_out > buffer %sKB" % (self.sock_out.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) / 1024))

    def interaction(self):
        try:
            data, address = self.sock_in.recvfrom(2 ** 16)  # 2**15 is max UDP datagram size
            data = data.decode('utf-8')

        except socket.timeout:
            logger.debug("sleep")
            time.sleep(0.1)
            return

        logger.debug("msg from %s [sz: %sB]" % (address, len(data)))

        if data[0] == '$' and data[3:6] == "R20":
            logger.debug("got IUR request!")

            # First send the Installation parameters
            if len(self.installation) != 0:
                installation = self.installation[-1]
                logger.debug("sending installation: %s" % self.installation)
                self.sock_out.sendto(self.installation, (self.ip_out, self.port_out))
                time.sleep(0.5)

            # Second send the Runtime parameters
            if len(self.runtime) != 0:
                runtime = self.runtime[-1]
                logger.debug("sending runtime: %s" % self.runtime)
                self.sock_out.sendto(self.runtime, (self.ip_out, self.port_out))
                time.sleep(0.5)

            # Third send the SVP ...
            if len(self.ssp) == 0:
                # If we're running but haven't received an SVP yet, then we build a fake one to send back.
                # Useful in testing the Server mode since the library establishes comm's before starting to serve
                num_entries = 2
                depths = np.zeros(num_entries)
                speeds = np.zeros(num_entries)
                depths[0] = 0.0
                speeds[0] = 1500.0
                depths[1] = 12000.0
                speeds[1] = 1500.0
                logger.debug("making up a fake profile")
            else:
                logger.debug("sending svp")
                time.sleep(1.5)
                ssp = self.ssp[-1]
                self.sock_out.sendto(ssp, (self.ip_out, self.port_out))
                return
        else:
            logger.debug("received SSP")
            if isinstance(data, bytes):
                data = data.decode("utf-8")

            print(data)

            depths = None
            speeds = None
            count = 0
            header = False
            for l in data.splitlines():
                num_fields = len(l.split(","))
                if num_fields == 12:  # header
                    num_entries = int(l.split(",")[2])
                    depths = np.zeros(num_entries)
                    speeds = np.zeros(num_entries)
                    depths[count] = l.split(",")[7]
                    speeds[count] = l.split(",")[8]
                    header = True
                elif num_fields == 5:
                    if not header:
                        logger.warning("unable to parse received header")
                        return
                    depths[count] = l.split(",")[0]
                    speeds[count] = l.split(",")[1]
                count += 1

        ssp = self.create_binary_ssp(depths=depths, speeds=speeds)

        logger.debug("sending data: %s" % repr(ssp))
        time.sleep(1.5)
        self.sock_out.sendto(ssp, (self.ip_out, self.port_out))
        self.ssp.append(ssp)
        logger.debug("data sent")

    def create_binary_ssp(self, depths, speeds, d_res=1):
        logger.debug('creating a binary ssp')
        d_res = 1  # depth resolution
        # TODO: improve it with the received metadata
        # -- header
        svp = struct.pack("<BBHIIHHIIHH", 2, 0x55, 122, 20120403, 0, 0, 0, 20120403, 0, depths.size, d_res)
        # -- body
        for count in range(depths.size):
            depth = int(depths[count] * d_res / 0.01)
            speed = int(speeds[count] * 10)
            pair = struct.pack("<II", depth, speed)
            svp += pair
        # -- footer
        footer = struct.pack("<BH", 3, 0)  # Not bothering with checksum since SVP Editor ignores it anyway
        svp += footer
        return svp
