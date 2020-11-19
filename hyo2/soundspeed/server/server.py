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
        self.cli_protocol = None
        self.delivered_casts = 0
        self.force_send = Event()
        self.shutdown = Event()
        self.wait_time = 5

        self.svp_acquisition_time = None
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

        # ### Now checks for SIS/SIS5 settings ###

        # Force user to select either SIS4 or SIS5
        if self.prj.use_sis4() and self.prj.use_sis5():
            logger.error("Both SIS4 and SIS5 listeners active. Select one for server mode.")
            self.prj.progress.end()
            return False

        # Check SIS
        sis4_check = True
        if self.prj.use_sis4():

            # - depth datagram
            if self.prj.listeners.sis4.xyz88:
                logger.info("SIS4 DEPTH broadcast: OK")
            else:
                logger.warning("SIS4 DEPTH broadcast: KO > SIS4 may warn about surface sound speed")

            # - navigation datagram
            if self.prj.listeners.sis4.nav:
                logger.info("SIS4 NAV broadcast: OK")
            else:
                logger.error("SIS4 NAV broadcast: KO")
                sis4_check = False

        else:
            sis4_check = False

        # Check SIS5
        sis5_check = True
        if self.prj.use_sis5():

            # - depth datagram
            if self.prj.listeners.sis5.mrz:
                logger.info("SIS5 MRZ broadcast: OK")
            else:
                logger.warning("SIS5 MRZ broadcast: KO > SIS5 may warn about surface sound speed")

            # - navigation datagram
            if self.prj.listeners.sis5.spo:
                logger.info("SIS5 SPO broadcast: OK")
            else:
                logger.error("SIS5 SPO broadcast: KO")
                sis5_check = False

        else:
            sis5_check = False

        # Select listener
        if (sis4_check is False) and (sis5_check is False):
            logger.error("SIS4/SIS5 listener check failed")
            self.prj.progress.end()
            return False
        elif (sis4_check is True) and (sis5_check is False):
            logger.info("SIS4 listener active")
            self.cli_protocol = "SIS"
        elif (sis4_check is False) and (sis5_check is True):
            logger.info("SIS5 listener active")
            self.cli_protocol = "KCTRL"

        self.prj.progress.update(60)

        # ### Test clients interaction (only SIS4/5 currently) ###

        prog_quantum = 40 / (len(self.prj.setup.client_list.clients) + 1)
        logger.info("Testing clients for reception-confirmation interaction")
        num_live_clients = 0
        for client in self.prj.setup.client_list.clients:

            if client.protocol != self.cli_protocol:
                client.alive = False
                continue

            if self.cli_protocol == "SIS":
                client.request_profile_from_sis4(self.prj)

                if self.prj.listeners.sis4.ssp:
                    logger.info("Interaction test: OK")
                    client.alive = True
                    num_live_clients += 1

                else:
                    logger.warning("Interaction test: KO")
                    client.alive = False

            if self.cli_protocol == "KCTRL":
                client.request_profile_from_sis5(self.prj)

                if self.prj.listeners.sis5.svp:
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

        if self.cli_protocol == "SIS":
            lat = self.prj.listeners.sis4.nav.latitude
            lon = self.prj.listeners.sis4.nav.longitude
            tm = self.prj.listeners.sis4.nav.dg_time
        elif self.cli_protocol == "KCTRL":
            lat = self.prj.listeners.sis5.spo.latitude
            lon = self.prj.listeners.sis5.spo.longitude
            tm = self.prj.listeners.sis5.spo.sensor_datetime
        else:
            logger.error("Shouldn't be able to reach here. Return Error")
            return

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
            lat_idx, lon_idx = self.prj.atlases.rtofs.grid_coords(lat=lat, lon=lon, dtstamp=tm, server_mode=True)
        elif self.prj.setup.server_source == 'GoMOFS':  # GoMOFS case
            lat_idx, lon_idx = self.prj.atlases.gomofs.grid_coords(lat=lat, lon=lon, dtstamp=tm, server_mode=True)
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

            if self.cli_protocol == "SIS":
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

            if self.cli_protocol == "KCTRL":
                if self.prj.listeners.sis5.mrz is None:
                    logger.warning("Unable to retrieve mrz datagram > Waiting %s secs"
                                   % self.wait_time)
                    count = 0
                    while count < self.wait_time:
                        time.sleep(1)
                        count += 1
                    return

                if self.prj.listeners.sis5.mrz.tss:
                    tss = self.prj.listeners.sis5.mrz.tss
                    if self.tss_last:
                        tss_diff = abs(tss - self.tss_last)
                if self.prj.listeners.sis5.mrz.transducer_draft:
                    draft = self.prj.listeners.sis5.mrz.transducer_draft

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
            self.prj.ssp = self.prj.atlases.woa09.query(lat=lat, lon=lon, dtstamp=tm, server_mode=True)

        elif self.prj.setup.server_source == 'WOA13':  # WOA09 case
            self.prj.ssp = self.prj.atlases.woa13.query(lat=lat, lon=lon, dtstamp=tm, server_mode=True)

        elif self.prj.setup.server_source == 'RTOFS':  # RTOFS case
            self.prj.ssp = self.prj.atlases.rtofs.query(lat=lat, lon=lon, dtstamp=tm, server_mode=True)

        elif self.prj.setup.server_source == 'GoMOFS':  # GoMOFS case
            self.prj.ssp = self.prj.atlases.gomofs.query(lat=lat, lon=lon, dtstamp=tm, server_mode=True)

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

                if self.cli_protocol == "SIS":
                    client.request_profile_from_sis4(prj=self.prj)
                    if not self.prj.listeners.sis4.ssp:
                        logger.info("client %s dead since last tx" % client.name)
                        client.alive = False
                        continue
                    else:
                        self.svp_acquisition_time = self.prj.listeners.sis4.ssp.acquisition_time

                if self.cli_protocol == "KCTRL":
                    client.request_profile_from_sis5(prj=self.prj)
                    if not self.prj.listeners.sis5.svp:
                        logger.info("client %s dead since last tx" % client.name)
                        client.alive = False
                        continue
                    else:
                        self.svp_acquisition_time = self.prj.listeners.sis5.svp.acquisition_time

                logger.info("Live client: %s" % client.name)
                num_live_clients += 1

                # test by comparing the times

                if self.prj.setup.client_list.last_tx_time != self.svp_acquisition_time:
                    logger.error("Times mismatch > %s != %s"
                                 % (self.prj.setup.client_list.last_tx_time,
                                    self.svp_acquisition_time))
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
