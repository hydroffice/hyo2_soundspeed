import time
import socket
import traceback
import logging

from hyo2.soundspeed.profile.dicts import Dicts
from hyo2.soundspeed.formats.writers.asvp import Asvp
from hyo2.soundspeed.formats.writers.calc import Calc

logger = logging.getLogger(__name__)


class Client:
    UDP_DATA_LIMIT = (2 ** 16) - 28

    def __init__(self, client):
        # print(client)
        self.name = client.split(":")[0]
        self.ip = client.split(":")[1]
        self.port = int(client.split(":")[2])
        self.protocol = client.split(":")[3]
        self.alive = True
        # logger.info("client: %s(%s:%s) %s" % (self.name, self.ip, self.port, self.protocol))

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
            if prj.setup.sis4_auto_apply_manual_casts or prj.setup.sis5_auto_apply_manual_casts or server_mode:
                kng_fmt = Dicts.kng_formats['S01']
            else:
                kng_fmt = Dicts.kng_formats['S12']
        if (self.protocol == "QINSY") or (self.protocol == "PDS2000"):
            kng_fmt = Dicts.kng_formats['S12']
            logger.info("forcing S12 format")

        apply_thin = True
        apply_12k = True
        tolerances = [0.1, 0.5]
        if self.protocol == "QINSY":
            apply_12k = False
            tolerances = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]

        tx_data = None
        for tolerance in tolerances:

            if not prj.prepare_sis(apply_thin=apply_thin, apply_12k=apply_12k, thin_tolerance=tolerance):
                logger.info("issue in preparing the data")
                return False

            asvp = Asvp()
            tx_data = asvp.convert(prj.ssp, fmt=kng_fmt)
            # print(tx_data)
            tx_data_size = len(tx_data)
            logger.debug("tx data size: %d (with tolerance: %.3f)" % (tx_data_size, tolerance))
            if tx_data_size < self.UDP_DATA_LIMIT:
                break

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
            if isinstance(tx_data, bytes):
                sock_out.sendto(tx_data, (self.ip, self.port))
            elif isinstance(tx_data, str):
                sock_out.sendto(tx_data.encode(), (self.ip, self.port))
            else:
                raise RuntimeError("invalid type of data to tx: %s" % type(tx_data))

        except socket.error as e:
            sock_out.close()
            traceback.print_exc()
            logger.warning("socket issue: %s" % e)
            return False

        sock_out.close()
        return True

    def request_profile_from_sis(self, prj):
        if self.protocol != "SIS":
            return

        prj.listeners.sis4.request_iur(ip=self.ip, port=self.port)
        wait = prj.setup.rx_max_wait_time
        count = 0
        quantum = 2
        logger.info("Waiting ..")
        while (count < wait) and (not prj.listeners.sis4.ssp) and (not prj.listeners.sis5.svp):
            time.sleep(quantum)
            count += quantum
            logger.info(".. %s sec" % count)
