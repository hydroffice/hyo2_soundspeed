from __future__ import absolute_import, division, print_function, unicode_literals

import time
import socket
import logging

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.profile.dicts import Dicts
from hydroffice.soundspeed.formats.writers.asvp import Asvp
from hydroffice.soundspeed.formats.writers.calc import Calc


class Client(object):
    def __init__(self, client):
        # print(client)
        self.name = client.split(":")[0]
        self.ip = client.split(":")[1]
        self.port = int(client.split(":")[2])
        self.protocol = client.split(":")[3]
        self.alive = True
        logger.info("client: %s(%s:%s) %s" % (self.name, self.ip, self.port, self.protocol))

    def send_cast(self, prj, server_mode=False):
        """Send a cast to the """
        if not self.alive:
            logger.debug("%s[%s:%s:%s] is NOT alive" % (self.name, self.ip, self.port, self.protocol))
            return False

        logger.info("transmitting to %s: [%s:%s:%s]" % (self.name, self.ip, self.port, self.protocol))

        success = False
        if self.protocol == "HYPACK":
            success = self.send_hyp_format(prj=prj)
        else:
            success = self.send_kng_format(prj=prj, server_mode=server_mode)

        return success

    def send_kng_format(self, prj, server_mode=False):
        logger.info("using kng format")
        kng_fmt = None
        if self.protocol == "SIS":
            if prj.setup.sis_auto_apply_manual_casts or server_mode:
                kng_fmt = Dicts.kng_formats['S01']
            else:
                kng_fmt = Dicts.kng_formats['S12']
        if (self.protocol == "QINSY") or (self.protocol == "PDS2000"):
            kng_fmt = Dicts.kng_formats['S12']
            logger.info("forcing S12 format")

        if not prj.prepare_sis():
            logger.info("issue in preparing the data")
            return False

        asvp = Asvp()
        tx_data = asvp.convert(prj.ssp, fmt=kng_fmt)
        # print(tx_data)

        return self._transmit(tx_data)

    def send_hyp_format(self, prj):
        logger.info("using hyp format")
        calc = Calc()
        tx_data = calc.convert(prj.ssp)
        return self._transmit(tx_data)

    def _transmit(self, tx_data):
        sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2 ** 16)
            sock_out.sendto(tx_data, (self.ip, self.port))

        except socket.error:
            sock_out.close()
            return False

        sock_out.close()
        return True

    def request_profile_from_sis(self, prj):
        if self.protocol != "SIS":
            return

        prj.listeners.sis.request_iur(ip=self.ip, port=self.port)
        wait = prj.setup.rx_max_wait_time
        count = 0
        quantum = 2
        logger.info("Waiting ..")
        while (count < wait) and (not prj.listeners.sis.ssp):
            time.sleep(quantum)
            count += quantum
            logger.info(".. %s sec" % count)
