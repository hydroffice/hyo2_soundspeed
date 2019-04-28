from typing import Optional
import time
from threading import Thread, Event
import logging

logger = logging.getLogger(__name__)


class Server(Thread):

    # noinspection PyUnresolvedReferences
    def __init__(self, prj: Optional['hyo2.soundspeed.soundspeed.SoundSpeedLibrary']):
        Thread.__init__(self, target=None, name="Synthetic Profile Server")
        self.prj = prj
        self.delivered_casts = 0
        self.force_send = Event()
        self.shutdown = Event()
        self.wait_time = 5

        self.tss_last = None
        self.lat_idx_last = None
        self.lon_idx_last = None

    def check_settings(self) -> bool:
        """Check the server settings"""

        logger.debug("checking settings ...")
        self.prj.progress.start(text='Check settings')

        # ### First checks for atlas sources ###

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

        self.prj.progress.update(30)

        # ### Now checks for SIS settings ###

        if not self.prj.use_sis4():
            logger.error("SIS-use check: KO")
            self.prj.progress.end()
            return False

        # - navigation datagram
        if self.prj.listeners.sis4.nav:
            logger.info("SIS NAV broadcast: OK")

        else:
            logger.error("SIS NAV broadcast: KO")
            self.prj.progress.end()
            return False

        # - depth datagram
        if self.prj.listeners.sis4.xyz88:
            logger.info("SIS DEPTH broadcast: OK")

        else:
            logger.warning("SIS DEPTH broadcast: KO > SIS may warn about surface sound speed")

        self.prj.progress.update(60)

        # ### Test clients interaction (only SIS currently) ###

        prog_quantum = 40 / (len(self.prj.setup.client_list.clients) + 1)
        logger.info("Testing clients for reception-confirmation interaction")
        num_live_clients = 0
        for client in self.prj.setup.client_list.clients:

            if client.protocol != "SIS":
                client.alive = False
                continue

            client.request_profile_from_sis4(self.prj)

            if self.prj.listeners.sis4.ssp:
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
        # if self.lib.vessel_draft is None:
        #     log.info("Vessel draft: %s (server)" % self.server_vessel_draft)
        # else:
        #     log.error("Vessel draft: %s" % self.lib.vessel_draft)
        #
        # # reset server flags
        # self.update_plot = False

        self.force_send = False
        self.delivered_casts = 0

        self.prj.progress.end()
        logger.debug("checking settings: OK")
        return True

    def run(self) -> None:
        """Start the simulation"""
        # self.init_logger()
        logger.debug("%s -> started" % self.name)

        count = 0
        while True:
            if self.shutdown.is_set():
                logger.debug("shutdown")
                break
            if (count % 100) == 0:
                logger.debug("#%05d: running" % count)

            try:
                self.check()
            except Exception as e:
                logger.warning("issue while retrieving synthetic data: %s" % e)

            time.sleep(3)
            count += 1

        logger.debug("%s -> ended" % self.name)

    def check(self) -> None:
        # ### Retrieve current location/time ###

        lat = self.prj.listeners.sis4.nav.latitude
        lon = self.prj.listeners.sis4.nav.longitude
        tm = self.prj.listeners.sis4.nav.dg_time
        if (lat is None) or (lon is None) or (tm is None):
            logger.warning("Possible corrupted reception of spatial timestamp > Waiting %s secs"
                           % self.wait_time)
            count = 0
            while count < self.wait_time:
                time.sleep(1)
                count += 1
            return
        logger.debug('loc/timestamp: (%s %s) @%s' % (lat, lon, tm.strftime('%Y/%m/%d %H:%M')))

        # ### Retrieve grid index ###

        if self.prj.setup.server_source == 'WOA09':  # WOA09 case
            lat_idx, lon_idx = self.prj.atlases.woa09.grid_coords(lat=lat, lon=lon)
        elif self.prj.setup.server_source == 'WOA13':  # WOA13 case
            lat_idx, lon_idx = self.prj.atlases.woa13.grid_coords(lat=lat, lon=lon)
        elif self.prj.setup.server_source == 'RTOFS':  # RTOFS case
            lat_idx, lon_idx = self.prj.atlases.rtofs.grid_coords(lat=lat, lon=lon, datestamp=tm, server_mode=True)
        elif self.prj.setup.server_source == 'GoMOFS':  # GoMOFS case
            lat_idx, lon_idx = self.prj.atlases.gomofs.grid_coords(lat=lat, lon=lon, datestamp=tm, server_mode=True)
        else:
            raise RuntimeError('unable to understand server source: %s' % self.prj.setup.server_source)
        # logger.debug('lat idx: %s [last: %s]' % (lat_idx, self.lat_idx_last))
        # logger.debug('lon idx: %s [last: %s]' % (lon_idx, self.lon_idx_last))
        if (lat_idx is None) or (lon_idx is None):
            logger.warning("grid index is invalid: (%s %s) -> out of model bounding box?" % (lat_idx, lon_idx))
            return

        # ### Retrieve surface sound speed (optional) ###

        tss = None
        draft = None
        tss_diff = 0.0
        if self.prj.setup.server_apply_surface_sound_speed:

            if self.prj.listeners.sis4.xyz88 is None:
                logger.warning("Unable to retrieve xyz88 datagram > Waiting %s secs"
                               % self.wait_time)
                count = 0
                while count < self.wait_time:
                    time.sleep(1)
                    count += 1
                return

            if self.prj.listeners.sis4.xyz88.sound_speed:
                tss = self.prj.listeners.sis4.xyz88.sound_speed
                if self.tss_last:
                    tss_diff = abs(tss - self.tss_last)
            if self.prj.listeners.sis4.xyz88.transducer_draft:
                draft = self.prj.listeners.sis4.xyz88.transducer_draft

        logger.debug('TSS delta: %s' % tss_diff)

        # check if we need a new cast
        if (tss_diff < 1.0) and (lat_idx == self.lat_idx_last) and (lon_idx == self.lon_idx_last):
            if self.force_send:
                logger.debug('Forcing profile transmission')
                self.force_send = False
            else:
                logger.debug('New profile not required')
                return

        # retrieve profile
        if self.prj.setup.server_source == 'WOA09':  # WOA09 case
            self.prj.ssp = self.prj.atlases.woa09.query(lat=lat, lon=lon, datestamp=tm, server_mode=True)

        elif self.prj.setup.server_source == 'WOA13':  # WOA09 case
            self.prj.ssp = self.prj.atlases.woa13.query(lat=lat, lon=lon, datestamp=tm, server_mode=True)

        elif self.prj.setup.server_source == 'RTOFS':  # RTOFS case
            self.prj.ssp = self.prj.atlases.rtofs.query(lat=lat, lon=lon, datestamp=tm, server_mode=True)

        elif self.prj.setup.server_source == 'GoMOFS':  # GoMOFS case
            self.prj.ssp = self.prj.atlases.gomofs.query(lat=lat, lon=lon, datestamp=tm, server_mode=True)

        else:
            raise RuntimeError('unable to understand server source: %s' % self.prj.setup.server_source)

        if not self.prj.has_ssp():
            logger.warning("Unable to retrieve a synthetic cast > Continue the loop")
            return

        logger.debug('Retrieve new synthetic profile')

        # apply tss (if required)
        if self.prj.setup.server_apply_surface_sound_speed and tss and draft:
            self.prj.add_cur_tss(server_mode=True)

        # after the first tx, a cast from SIS is always required
        num_live_clients = 0
        if self.prj.setup.client_list.last_tx_time:
            logger.info("Requesting cast from SIS (prior to transmission)")

            for client in self.prj.setup.client_list.clients:

                # skipping dead clients
                if not client.alive:
                    logger.info("Dead client: %s > Skipping" % client.ip)
                    continue

                client.request_profile_from_sis4(prj=self.prj)
                if not self.prj.listeners.sis4.ssp:
                    logger.info("client %s dead since last tx" % client.name)
                    client.alive = False
                    continue

                logger.info("Live client: %s" % client.name)
                num_live_clients += 1

                # test by comparing the times
                if self.prj.setup.client_list.last_tx_time != self.prj.listeners.sis4.ssp.acquisition_time:
                    logger.error("Times mismatch > %s != %s"
                                 % (self.prj.setup.client_list.last_tx_time,
                                    self.prj.listeners.sis4.ssp.acquisition_time))
                    self.shutdown.set()
                    return

            if num_live_clients == 0:
                self.shutdown.set()
                logger.error("no live clients")
                return

        self.prj.setup.client_list.transmit_ssp(prj=self.prj, server_mode=True)
        if self.prj.setup.server_apply_surface_sound_speed:
            self.tss_last = tss  # store the tss for the next iteration

        self.lat_idx_last = lat_idx
        self.lon_idx_last = lon_idx

        if not self.prj.store_data():
            logger.warning("Unable to save to db!")
            return

    def stop(self) -> None:
        self.shutdown.set()
