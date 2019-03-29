import numpy as np
import time
import logging
from typing import TYPE_CHECKING, Union

from hyo2.soundspeed.client.client import Client
if TYPE_CHECKING:
    from hyo2.soundspeed.soundspeed import SoundSpeedLibrary

logger = logging.getLogger(__name__)


class ClientList:
    def __init__(self):
        self.num_clients = 0
        self.clients = list()
        self.last_tx_time = None

    def add_client(self, client: str):
        client = Client(client)
        self.clients.append(client)
        self.num_clients += 1

    def transmit_ssp(self, prj: 'SoundSpeedLibrary', server_mode: bool = False):

        prj.progress.start(text='Transmitting', is_disabled=server_mode, has_abortion=True)

        # loop through the client list
        success = True  # false if one tx has troubles
        prog_quantum = 100 / (len(self.clients) + 1)
        for client in self.clients:

            # clean previously received profile from SIS
            if client.protocol == "SIS":
                prj.listeners.sis4.ssp = None
            elif client.protocol == "KCTRL":
                prj.listeners.sis5.svp = None

            prj.progress.add(prog_quantum)

            if not client.send_cast(prj=prj, server_mode=server_mode):
                logger.warning('unable to send profile to %s' % client.name)
                success = False
                continue

            if client.protocol not in ["SIS", "KCTRL"]:
                logger.info("transmitted cast, protocol %s does not allow verification"
                            % client.protocol)
                time.sleep(1)
                if not server_mode:
                    prj.cb.msg_tx_no_verification(name=client.name, protocol=client.protocol)
                continue

            if not prj.setup.sis_auto_apply_manual_casts:
                logger.info("transmitted cast, SIS is waiting for operator confirmation")
                if not server_mode:
                    prj.cb.msg_tx_sis_wait(name=client.name)
                continue

            logger.debug("waiting for receipt confirmation...")
            wait = 0
            wait_max = prj.setup.rx_max_wait_time
            # For multiple SIS clients, make sure the client IP match with the sender IP.
            while True:
                if (wait > wait_max) or (prj.listeners.sis4.ssp is not None) or (prj.listeners.sis5.svp is not None):
                    break

                time.sleep(1)
                wait += 1
                logger.debug("waiting for %s sec" % wait)

                prj.progress.update()
                if prj.progress.canceled:
                    logger.info("canceled by user")
                    wait = wait_max

            if (client.protocol == "SIS") and prj.listeners.sis4.ssp:
                # The KM .all SVP datagrams have a bug in their time reporting and
                # have a 100 second granularity so can't compare times
                # to ensure it's the same profile.  Comparing the sound speeds instead
                d_tx = prj.cur.sis.depth[prj.cur.sis_thinned]
                s_tx = prj.cur.sis.speed[prj.cur.sis_thinned]
                # print(d_tx, s_tx)
                s_rx = np.interp(d_tx, prj.listeners.sis4.ssp.depth, prj.listeners.sis4.ssp.speed)
                max_diff = max(abs(s_tx - s_rx))
                if max_diff < 0.2:
                    self.last_tx_time = prj.listeners.sis4.ssp.acquisition_time
                    logger.debug("reception confirmed: %s" % self.last_tx_time.strftime("%d/%m/%Y, %H:%M:%S"))
                    if not server_mode:
                        prj.cb.msg_tx_sis_confirmed(name=client.name)
                    continue
                else:
                    logger.info("casts differ by %.2f m/s" % max_diff)
                    if not server_mode:
                        prj.cb.msg_tx_sis_not_confirmed(name=client.name, ip=prj.setup.sis4_listen_port)
                    success = False
                    continue

            elif (client.protocol == "KCTRL") and prj.listeners.sis5.svp:
                # Comparing the sound speeds instead
                d_tx = prj.cur.sis.depth[prj.cur.sis_thinned]
                s_tx = prj.cur.sis.speed[prj.cur.sis_thinned]
                # print(d_tx, s_tx)
                s_rx = np.interp(d_tx, prj.listeners.sis5.svp.depth, prj.listeners.sis5.svp.speed)
                max_diff = max(abs(s_tx - s_rx))
                if max_diff < 0.2:
                    self.last_tx_time = prj.listeners.sis5.svp.acquisition_time
                    logger.debug("reception confirmed: %s" % self.last_tx_time.strftime("%d/%m/%Y, %H:%M:%S"))
                    if not server_mode:
                        prj.cb.msg_tx_sis_confirmed(name=client.name)
                    continue
                else:
                    logger.info("casts differ by %.2f m/s" % max_diff)
                    if not server_mode:
                        prj.cb.msg_tx_sis_not_confirmed(name=client.name, ip=prj.setup.sis5_listen_port)
                    success = False
                    continue

            else:
                logger.warning("reception NOT confirmed: unable to catch the back datagram")
                if not server_mode:
                    prj.cb.msg_tx_sis_not_confirmed(name=client.name, ip=prj.setup.sis4_listen_port)
                success = False

        prj.progress.end()
        return success
