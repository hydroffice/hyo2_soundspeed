from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from ..profile.dicts import Dicts
from .client import Client


class ClientList(object):
    def __init__(self):
        self.num_clients = 0
        self.clients = []
        self.last_tx_time = None

    def add_client(self, client):
        client = Client(client)
        self.clients.append(client)
        self.num_clients += 1

    def transmit_ssp(self, prj):

        prj.progress.start('Transmitting')

        # loop through the client list
        success = True  # false if one tx has troubles
        prog_quantum = 100 / (len(self.clients) + 1)
        for client in self.clients:

            # clean previously received profile from SIS
            if client.protocol != "SIS":
                prj.listeners.sis.ssp = None

            prj.progress.add(prog_quantum)

            if not client.send_cast(prj=prj):
                logger.warning('unable to send profile to %s' % client.name)
                success = False
                continue

            if client.protocol != "SIS":
                logger.info("transmitted cast, protocol %s does not allow verification"
                            % client.protocol)
                time.sleep(1)
                prj.cb.msg_tx_no_verification(name=client.name, protocol=client.protocol)
                continue

            if not prj.setup.sis_auto_apply_manual_casts:
                logger.info("transmitted cast, SIS is waiting for operator confirmation")
                prj.cb.msg_tx_sis_wait(name=client.name)
                continue

            logger.debug("waiting for receipt confirmation...")
            wait = 0
            wait_max = prj.setup.rx_max_wait_time
            while (not prj.listeners.sis.ssp) and (wait < wait_max):
                time.sleep(1)
                wait += 1
                logger.debug("waiting for %s sec" % wait)

            if prj.listeners.sis.ssp:
                # The KM SVP datagrams have a bug in their time reporting and
                # have a 100 second granularity so can't compare times
                # to ensure it's the same profile.  Comparing the sound speeds instead
                d_tx = prj.cur.sis.depth[prj.cur.sis_thinned]
                s_tx = prj.cur.sis.speed[prj.cur.sis_thinned]
                # print(d_tx, s_tx)
                s_rx = np.interp(d_tx, prj.listeners.sis.ssp.depth, prj.listeners.sis.ssp.speed)
                max_diff = max(abs(s_tx - s_rx))
                if max_diff < 0.2:
                    self.last_tx_time = prj.listeners.sis.ssp.acquisition_time
                    logger.debug("reception confirmed: %s" % self.last_tx_time.strftime("%d/%m/%Y, %H:%M:%S"))
                    prj.cb.msg_tx_sis_confirmed(name=client.name)
                    continue
                else:
                    logger.info("casts differ by %.2f m/s" % max_diff)
                    prj.cb.msg_tx_sis_not_confirmed(name=client.name, ip=prj.setup.sis_listen_port)
                    success = False
                    continue
            else:
                logger.warning("reception NOT confirmed: unable to catch the back datagram")
                prj.cb.msg_tx_sis_not_confirmed(name=client.name, ip=prj.setup.sis_listen_port)
                success = False

        prj.progress.end()
        return success
