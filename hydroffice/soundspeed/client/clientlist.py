from __future__ import absolute_import, division, print_function, unicode_literals

import time
import logging

logger = logging.getLogger(__name__)

from ..profile.dicts import Dicts
from .client import Client


class ClientList(object):
    def __init__(self):
        self.num_clients = 0
        self.clients = []

    def add_client(self, client):
        client = Client(client)
        self.clients.append(client)
        self.num_clients += 1

    def transmit_ssp(self, prj):

        # loop through the client list
        success = True  # false if one tx has troubles
        for client in self.clients:

            # clean previously received profile from SIS
            if client.protocol != "SIS":
                prj.listeners.sis.ssp = None

            if not client.send_cast(prj=prj):
                logger.warning('unable to send profile to %s' % client.name)
                success = False
                continue

            if client.protocol != "SIS":
                logger.info("transmitted cast, protocol %s does not allow verification"
                            % client.protocol)
                time.sleep(1)
                continue

            logger.debug("waiting for receipt confirmation...")
            wait = 0
            wait_max = prj.setup.rx_max_wait_time
            while (not prj.listeners.sis.ssp) and (wait < wait_max):
                time.sleep(1)
                wait += 1
                logger.debug("waiting for %s sec" % wait)

            if prj.listeners.sis.ssp:
                logger.debug("reception confirmed")
                success = True
            else:
                logger.warning("reception NOT confirmed: unable to catch the back datagram")
                success = False

        return success
