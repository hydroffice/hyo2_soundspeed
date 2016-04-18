from __future__ import absolute_import, division, print_function, unicode_literals

import time
import os
from threading import Thread, Event
import logging

logger = logging.getLogger(__name__)

from ..profile.dicts import Dicts


class Server(Thread):
    def __init__(self, prj, target=None, name="server"):
        Thread.__init__(self, target=target, name=name)
        self.name = name
        self.desc = "server"
        self.prj = prj
        self.delivered_casts = 0
        self.force_send = Event()
        self.shutdown = Event()
        self.wait_time = 5

    def stop(self):
        self.shutdown.set()

    def check_settings(self):
        """Check the server settings"""

        self.prj.progress.start('Check settings')

        # server sources
        if self.prj.setup.server_source == 'RTOFS':  # RTOFS case
            if self.prj.use_rtofs():
                logger.info("RTOFS-use check: OK")
            else:
                logger.error("RTOFS-use check: KO")
                self.prj.progress.end()
                return False
        if self.prj.setup.server_source == 'WOA09':  # WOA09 case
            if self.prj.use_woa09():
                logger.info("WOA09-use check: OK")
            else:
                logger.error("WOA09-use check: KO")
                self.prj.progress.end()
                return False
        if self.prj.setup.server_source == 'WOA13':  # WOA09 case
            if self.prj.use_woa13():
                logger.info("WOA13-use check: OK")
            else:
                logger.error("WOA13-use check: KO")
                self.prj.progress.end()
                return False

        # Check for SIS
        if not self.prj.use_sis():
            logger.error("SIS-use check: KO")
            self.prj.progress.end()
            return False
        # - navigation datagram
        if self.prj.listeners.sis.nav:
            logger.info("SIS NAV broadcast: OK")
        else:
            logger.error("SIS NAV broadcast: KO")
            self.prj.progress.end()
            return False
        # - depth datagram
        if self.prj.listeners.sis.xyz88:
            logger.info("SIS DEPTH broadcast: OK")
        else:
            logger.warning("SIS DEPTH broadcast: KO > SIS may warn about surface sound speed")

        self.prj.progress.update(20)

        # Test clients interaction
        prog_quantum = 80 / (len(self.prj.setup.client_list.clients) + 1)
        logger.info("Testing clients for reception-confirmation interaction")
        num_live_clients = 0
        for client in self.prj.setup.client_list.clients:
            if client.protocol != "SIS":
                client.alive = False
                continue

            client.request_profile_from_sis(self.prj)
            if self.prj.listeners.sis.ssp:
                logger.info("Interaction test: OK")
                client.alive = True
                num_live_clients += 1
            else:
                logger.warning("Interaction test: KO")
                client.alive = False

            self.prj.progress.add(prog_quantum)

        if num_live_clients == 0:
            logger.error("Unable to confirm interaction with any clients > The Server Mode is not available")
            self.prj.progress.end()
            return False
        else:
            logger.info("Interaction verified with %s client/clients" % num_live_clients)

        # # test vessel draft
        # if self.prj.vessel_draft is None:
        #     log.info("Vessel draft: %s (server)" % self.server_vessel_draft)
        # else:
        #     log.error("Vessel draft: %s" % self.prj.vessel_draft)
        #
        # # reset server flags
        # self.update_plot = False

        self.force_send = False
        self.delivered_casts = 0

        self.prj.progress.end()
        return True

    def run(self):
        """Start the simulation"""
        # self.init_logger()
        logger.debug("%s start" % self.name)

        count = 0
        while True:
            if self.shutdown.is_set():
                logger.debug("shutdown")
                break
            if (count % 100) == 0:
                logger.debug("#%05d: running" % count)

            self.check()

            time.sleep(10)
            count += 1

        logger.debug("%s end" % self.name)

    def check(self):
        # retrieve current location/time
        lat = self.prj.listeners.sis.nav.latitude
        lon = self.prj.listeners.sis.nav.longitude
        tm = self.prj.listeners.sis.nav.dg_time
        if (lat is None) or (lon is None) or (tm is None):
            logger.warning("Possible corrupted reception of spatial timestamp > Waiting %s secs"
                           % self.wait_time)
            count = 0
            while count < self.wait_time:
                time.sleep(1)
                count += 1
            return
        logger.debug('loc/timestamp: (%s %s)/%s' % (lat, lon, tm.strftime('%Y/%m/%d %H:%M')))

        # retrieve profile
        if self.prj.setup.server_source == 'RTOFS':  # RTOFS case
            self.prj.ssp = self.prj.atlases.rtofs.query(lat=lat, lon=lon, datestamp=tm, server_mode=True)
        elif self.prj.setup.server_source == 'WOA09':  # WOA09 case
            self.prj.ssp = self.prj.atlases.woa09.query(lat=lat, lon=lon, datestamp=tm, server_mode=True)
        elif self.prj.setup.server_source == 'WOA13':  # WOA09 case
            self.prj.ssp = self.prj.atlases.woa13.query(lat=lat, lon=lon, datestamp=tm, server_mode=True)
        else:
            raise RuntimeError('unable to understand server source: %s' % self.prj.setup.server_source)

        if not self.prj.has_ssp():
            logger.warning("Unable to retrieve a synthetic cast > Continue the loop")
            return
        logger.debug('Retrieve new synthetic profile')


        # after the first tx, a cast from SIS is always required
        num_live_clients = 0
        if self.prj.setup.client_list.last_tx_time:
            # log.info("Requesting cast from SIS (prior to transmission)")
            #
            # for client in range(self.prj.s.client_list.num_clients):
            #
            #     # skipping dead clients
            #     if not self.prj.s.client_list.clients[client].alive:
            #         log.info("Dead client: %s > Skipping"
            #                  % self.prj.s.client_list.clients[client].IP)
            #         continue
            #
            #     # actually requiring the SSP
            #     self.prj.ssp_recipient_ip = self.prj.s.client_list.clients[client].IP
            #     log.info("Testing client: %s" % self.prj.ssp_recipient_ip)
            #     self.prj.get_cast_from_sis()
            #     log.info("Tested client and got %s" % self.prj.km_listener.ssp)
            #     if not self.prj.km_listener.ssp:
            #         log.info("Client went dead since last transmission %s" % self.prj.ssp_recipient_ip)
            #         self.prj.s.client_list.clients[client].alive = False
            #         continue
            #
            #     # test by comparing the times
            #     if self.last_sent_ssp_time != self.prj.km_listener.ssp.acquisition_time:
            #         log.warning("Times mismatch > %s != %s"
            #                     % (self.prj.time_of_last_tx, self.last_sent_ssp_time))
            #         self.stopped_on_error = True
            #         self.prj.server.error_message = "Times mismatch > Another agent uploaded SSP on SIS"
            #         log.error(self.prj.server.error_message)
            #         self.prj.s.client_list.clients[client].alive = False
            #         continue
            #
            #     log.info("Live client")
            #
            #     num_live_clients += 1
            #
            # if num_live_clients == 0:
            #     self.stopped_on_error = True
            #     self.prj.server.error_message = "No more live clients"
            #     log.error("Found no live clients during pre-transmission test")
            #     continue
            pass

        self.prj.setup.client_list.transmit_ssp(prj=self.prj, server_mode=True)

