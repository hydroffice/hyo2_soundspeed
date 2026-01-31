import logging
import os
import time
import traceback
from datetime import datetime
from threading import Thread, Event
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger(__name__)


class Server(Thread):

    # noinspection PyUnresolvedReferences
    def __init__(self, prj: Optional['SoundSpeedLibrary']):
        Thread.__init__(self, target=None, name="Synthetic Profile Server")
        self.prj = prj
        self.delivered_casts = 0
        self.force_send = False
        self.shutdown = Event()
        self.wait_time = 5

        self.last_tx_tss = None

        self.cur_lat = None  # type: Optional[float]
        self.cur_lon = None  # type: Optional[float]
        self.cur_tm = None  # type: Optional[datetime]
        self.cur_tss = None  # type: Optional[float]
        self.cur_draft = None  # type: Optional[float]
        self.cur_tss_diff = 0.0  # type: float
        self.cur_lat_idx = None  # type: Optional[int]
        self.cur_lon_idx = None  # type: Optional[int]

        self.last_lat_idx = None  # type: Optional[int]
        self.last_lon_idx = None  # type: Optional[int]

        self.cur_invalid_source_idx = 0
        self.max_invalid_source_idx = self.prj.setup.server_max_failed_attempts

        self.settings_errors = list()
        self.runtime_errors = list()

    def list_uni_clients(self) -> List[str]:
        uni_clients: List[str] = list()

        for client in self.prj.setup.client_list.clients:
            if client.protocol not in ["SIS", "KCTRL"]:
                uni_clients.append("%s [protocol: %s]" % (client.name, client.protocol))

        return uni_clients

    def check_settings(self, use_uni_clients: bool = False) -> bool:
        """Check the server settings"""

        logger.debug("Initialization checks ...")
        self.prj.progress.start(text='Check settings')
        self.settings_errors.clear()
        self.prj.setup.client_list.last_tx_time = None
        self.prj.setup.client_list.last_tx_time_2 = None

        # Check for atlas sources
        if not self._check_settings_source():
            self.prj.progress.end()
            return False

        self.prj.progress.update(30)

        # Check for SIS settings
        if not self._check_settings_sis():
            self.prj.progress.end()
            return False

        self.prj.progress.update(60)

        # Check for clients
        if not self._check_settings_clients(use_uni_clients=use_uni_clients):
            self.prj.progress.end()
            return False

        self.prj.progress.end()
        logger.debug("Initialization checks: OK")
        return True

    def _check_settings_source(self) -> bool:

        if self.prj.setup.server_source == 'WOA09':  # WOA09 case

            if self.prj.use_woa09():
                logger.info("WOA09-use check: OK")

            else:
                msg = "WOA09-use check: KO"
                logger.error(msg)
                self.settings_errors.append(msg)
                return False

        elif self.prj.setup.server_source == 'WOA13':  # WOA13 case

            if self.prj.use_woa13():
                logger.info("WOA13-use check: OK")

            else:
                msg = "WOA13-use check: KO"
                logger.error(msg)
                self.settings_errors.append(msg)
                return False

        elif self.prj.setup.server_source == 'WOA18':  # WOA18 case

            if self.prj.use_woa18():
                logger.info("WOA18-use check: OK")

            else:
                msg = "WOA18-use check: KO"
                logger.error(msg)
                self.settings_errors.append(msg)
                return False

        elif self.prj.setup.server_source == 'WOA23':  # WOA23 case

            if self.prj.use_woa23():
                logger.info("WOA23-use check: OK")

            else:
                msg = "WOA23-use check: KO"
                logger.error(msg)
                self.settings_errors.append(msg)
                return False

        elif self.prj.setup.server_source == 'RTOFS':  # RTOFS case

            if self.prj.use_rtofs():
                logger.info("RTOFS-use check: OK")

            else:
                msg = "RTOFS-use check: KO"
                logger.error(msg)
                self.settings_errors.append(msg)
                return False

        elif self.prj.setup.server_source == 'GoMOFS':  # GoMOFS case

            if self.prj.use_gomofs:
                logger.info("GoMOFS-use check: OK")

            else:
                msg = "GoMOFS-use check: KO"
                logger.error(msg)
                self.settings_errors.append(msg)
                return False

        else:
            msg = "Unsupported source: %s" % self.prj.setup.server_source
            logger.error(msg)
            self.settings_errors.append(msg)
            return False

        return True

    def _check_settings_sis(self) -> bool:

        if not self.prj.use_sis():
            msg = "SIS-use check: KO"
            logger.error(msg)
            self.settings_errors.append(msg)
            return False

        # - navigation datagram
        if self.prj.listeners.sis.nav:
            logger.info("SIS NAV broadcast: OK")

        else:
            msg = "SIS NAV broadcast: KO"
            logger.error(msg)
            self.settings_errors.append(msg)
            return False

        # - depth datagram
        if self.prj.listeners.sis.xyz:
            logger.info("SIS DEPTH broadcast: OK")
        else:
            logger.warning("SIS DEPTH broadcast: KO > SIS may warn about surface sound speed")

        return True

    def _check_settings_clients(self, use_uni_clients: bool = False) -> bool:

        prog_quantum = 40 / (len(self.prj.setup.client_list.clients) + 1)
        logger.info("Testing clients for reception-confirmation interaction")
        num_clients = 0
        for client in self.prj.setup.client_list.clients:

            client.alive = True

            if client.protocol not in ["SIS", "KCTRL"]:
                if use_uni_clients:
                    logger.info('Using unidirectional client: %s [%s]' % (client.name, client.protocol))
                    num_clients += 1
                else:
                    logger.info('Skipping unidirectional client: %s [%s]' % (client.name, client.protocol))
                    client.alive = False
                continue

            client.request_profile_from_sis(self.prj)

            if self.prj.listeners.sis.ssp:
                logger.info("Interaction test: OK")
                client.alive = True
                num_clients += 1

            else:
                logger.warning("Interaction test: KO")
                client.alive = False

            self.prj.progress.add(prog_quantum)

        if num_clients == 0:
            msg = "Unable to confirm clients."
            logger.error(msg)
            self.settings_errors.append(msg)
            return False

        else:
            logger.info("Interaction verified with %s client/clients" % num_clients)

        return True

    def run(self) -> None:
        """Start the simulation"""
        # self.init_logger()
        logger.debug("%s -> started" % self.name)
        self.runtime_errors.clear()

        self.force_send = False
        self.delivered_casts = 0

        count = 0
        while True:
            if self.shutdown.is_set():
                # reset alive all the clients
                for client in self.prj.setup.client_list.clients:
                    client.alive = True
                logger.debug("Shutdown Server Mode")
                break
            if (count % 100) == 0:
                logger.debug("#%05d: running" % count)

            try:
                self.check()
            except Exception as e:
                traceback.print_exc()
                msg = "While in Server Mode, %s" % e
                self.runtime_errors.append(msg)
                logger.error(e)
                self.shutdown.set()
                continue

            time.sleep(60)  # TODO
            count += 1

        logger.debug("%s -> ended" % self.name)

    def check(self) -> None:
        # Retrieve current location/time
        if not self._retrieve_cur_pos():
            return
        if not self._retrieve_cur_source_idx():
            return
        logger.debug('current location/time: (%s %s) @%s -> (%s, %s)'
                     % (self.cur_lat, self.cur_lon, self.cur_tm.strftime('%Y/%m/%d %H:%M:%S'),
                        self.cur_lat_idx, self.cur_lon_idx))

        self._retrieve_cur_tss()
        if self.cur_tss_diff:
            logger.debug('TSS delta: %.3f m/s' % self.cur_tss_diff)

        if not self._is_new_profile_required():
            return

        if self._has_sis_manual_profile():
            return

        if not self._retrieve_new_profile():
            return

        self._transmit_profile()

    def _retrieve_cur_pos(self) -> bool:

        max_attempts = 12
        cur_attempts = 0

        while True:
            self.cur_lat = self.prj.listeners.sis.nav_latitude
            self.cur_lon = self.prj.listeners.sis.nav_longitude
            self.cur_tm = self.prj.listeners.sis.nav_timestamp

            if (self.cur_lat is None) or (self.cur_lon is None) or (self.cur_tm is None):

                if cur_attempts < max_attempts:
                    logger.warning("Possible issues in retrieving current location and timestamp. "
                                   "Waiting %s secs (Ongoing attempt #%d/%d)"
                                   % (self.wait_time, cur_attempts, max_attempts))
                    cur_attempts += 1
                    count = 0
                    while count < self.wait_time:
                        time.sleep(1)
                        count += 1

                else:
                    self.shutdown.set()
                    msg = 'Unable to retrieve current location and timestamp after %s seconds' \
                          % (max_attempts * self.wait_time)
                    self.runtime_errors.append(msg)
                    logging.error(msg)
                    return False

            else:
                os.environ.get("SSM_DEBUG") and logger.debug("POS: %s, %s, %s" % (
                    self.cur_tm, self.cur_lat, self.cur_lon))

                # Commented to avoid issues when adding TSS
                # self.prj.listeners.sis.clear_nav()

                return True

    def _retrieve_cur_source_idx(self) -> bool:
        if self.prj.setup.server_source == 'WOA09':  # WOA09 case
            self.cur_lat_idx, self.cur_lon_idx = self.prj.atlases.woa09.grid_coords(lat=self.cur_lat, lon=self.cur_lon)
        elif self.prj.setup.server_source == 'WOA13':  # WOA13 case
            self.cur_lat_idx, self.cur_lon_idx = self.prj.atlases.woa13.grid_coords(lat=self.cur_lat, lon=self.cur_lon)
        elif self.prj.setup.server_source == 'WOA18':  # WOA18 case
            self.cur_lat_idx, self.cur_lon_idx = self.prj.atlases.woa18.grid_coords(lat=self.cur_lat, lon=self.cur_lon)
        elif self.prj.setup.server_source == 'WOA23':  # WOA23 case
            self.cur_lat_idx, self.cur_lon_idx = self.prj.atlases.woa23.grid_coords(lat=self.cur_lat, lon=self.cur_lon)
        elif self.prj.setup.server_source == 'RTOFS':  # RTOFS case
            self.cur_lat_idx, self.cur_lon_idx = self.prj.atlases.rtofs.grid_coords(lat=self.cur_lat, lon=self.cur_lon,
                                                                                    dtstamp=self.cur_tm,
                                                                                    server_mode=True)
        elif self.prj.setup.server_source == 'GoMOFS':  # GoMOFS case
            self.cur_lat_idx, self.cur_lon_idx = self.prj.atlases.gomofs.grid_coords(lat=self.cur_lat, lon=self.cur_lon,
                                                                                     dtstamp=self.cur_tm,
                                                                                     server_mode=True)
        else:
            raise RuntimeError('Unsupported source: %s' % self.prj.setup.server_source)

        # logger.debug('lat idx: %s [last: %s]' % (lat_idx, self.lat_idx_last))
        # logger.debug('lon idx: %s [last: %s]' % (lon_idx, self.lon_idx_last))
        if (self.cur_lat_idx is None) or (self.cur_lon_idx is None):
            self.cur_invalid_source_idx += 1
            if self.cur_invalid_source_idx >= self.max_invalid_source_idx:
                raise RuntimeError("Too many invalid attempts (%d) to retrieve a valid source index"
                                   % self.cur_invalid_source_idx)
            logger.warning("Source index is invalid: (%s %s) [%d/%d] -> "
                           "Is the vessel out of the selected source coverage?"
                           % (self.cur_lat_idx, self.cur_lon_idx,
                              self.cur_invalid_source_idx, self.max_invalid_source_idx))
            return False

        # reset the number of invalid source idx
        self.cur_invalid_source_idx = 0
        return True

    def _retrieve_cur_tss(self) -> None:

        self.cur_tss = None
        self.cur_draft = None
        self.cur_tss_diff = 0.0

        if self.prj.setup.server_apply_surface_sound_speed:

            if self.prj.listeners.sis.xyz is None:
                logger.warning("Unable to retrieve xyz datagram")
                return

            if self.prj.listeners.sis.xyz_transducer_sound_speed:
                self.cur_tss = self.prj.listeners.sis.xyz_transducer_sound_speed
                if self.last_tx_tss:
                    self.cur_tss_diff = abs(self.cur_tss - self.last_tx_tss)
            if self.prj.listeners.sis.xyz_transducer_depth:
                self.cur_draft = self.prj.listeners.sis.xyz_transducer_depth

            os.environ.get("SSM_DEBUG") and logger.debug("TSS: %s, %s [diff: %s]" % (
                self.cur_tss, self.cur_draft, self.cur_tss_diff))

            # Commented to avoid issues when adding TSS
            # self.prj.listeners.sis.clear_nav()

        # Commented to avoid issues when adding TSS
        # self.prj.listeners.sis.clear_xyz()

    def _is_new_profile_required(self):
        source_idx_changed = (self.cur_lat_idx != self.last_lat_idx) or (self.cur_lon_idx != self.last_lon_idx)
        if source_idx_changed:
            return True

        if self.cur_tss_diff >= 1.0:
            return True

        if self.force_send:
            logger.debug('Forcing the transmission of a synthetic profile')
            self.force_send = False
            return True

        logger.debug('New profile not required')
        return False

    def _has_sis_manual_profile(self) -> bool:
        # after the first tx, a cast from SIS is always required
        if not self.prj.setup.client_list.last_tx_time:
            return False

        logger.info("Requesting SIS current profile ...")
        num_clients = 0
        for client in self.prj.setup.client_list.clients:

            # skipping dead clients
            if not client.alive:
                logger.info("Dead client: %s [%s] > Skipping" % (client.ip, client.protocol))
                continue

            if client.protocol not in ["SIS", "KCTRL"]:
                num_clients += 1
                continue

            client.request_profile_from_sis(prj=self.prj)
            if not self.prj.listeners.sis.ssp:
                logger.info("Client %s dead since last tx" % client.name)
                client.alive = False
                continue

            logger.info("Live client: %s" % client.name)
            num_clients += 1

            # test by comparing the times
            if self.prj.setup.client_list.last_tx_time != self.prj.listeners.sis.ssp.acquisition_time:
                if self.prj.setup.client_list.last_tx_time_2 == self.prj.listeners.sis.ssp.acquisition_time:
                    logger.info('missed reception of last transmitted SSP -> '
                                'SIS is using the previously-transmitted SSP')
                else:
                    msg = "Times mismatch > %s AND %s != %s " \
                          % (self.prj.setup.client_list.last_tx_time, self.prj.setup.client_list.last_tx_time_2,
                             self.prj.listeners.sis.ssp.acquisition_time)
                    self.runtime_errors.append(msg)
                    logger.error(msg)
                    self.shutdown.set()
                    return True

        if num_clients == 0:
            msg = "No alive clients"
            self.runtime_errors.append(msg)
            logger.error(msg)
            self.shutdown.set()
            return True

        return False

    def _retrieve_new_profile(self) -> bool:
        # retrieve profile
        if self.prj.setup.server_source == 'WOA09':  # WOA09 case
            self.prj.ssp = self.prj.atlases.woa09.query(lat=self.cur_lat, lon=self.cur_lon, dtstamp=self.cur_tm,
                                                        server_mode=True)

        elif self.prj.setup.server_source == 'WOA13':  # WOA13 case
            self.prj.ssp = self.prj.atlases.woa13.query(lat=self.cur_lat, lon=self.cur_lon, dtstamp=self.cur_tm,
                                                        server_mode=True)

        elif self.prj.setup.server_source == 'WOA18':  # WOA18 case
            self.prj.ssp = self.prj.atlases.woa18.query(lat=self.cur_lat, lon=self.cur_lon, dtstamp=self.cur_tm,
                                                        server_mode=True)

        elif self.prj.setup.server_source == 'WOA23':  # WOA23 case
            self.prj.ssp = self.prj.atlases.woa23.query(lat=self.cur_lat, lon=self.cur_lon, dtstamp=self.cur_tm,
                                                        server_mode=True)

        elif self.prj.setup.server_source == 'RTOFS':  # RTOFS case
            self.prj.ssp = self.prj.atlases.rtofs.query(lat=self.cur_lat, lon=self.cur_lon, dtstamp=self.cur_tm,
                                                        server_mode=True)

        elif self.prj.setup.server_source == 'GoMOFS':  # GoMOFS case
            self.prj.ssp = self.prj.atlases.gomofs.query(lat=self.cur_lat, lon=self.cur_lon, dtstamp=self.cur_tm,
                                                         server_mode=True)

        else:
            raise RuntimeError('unable to understand server source: %s' % self.prj.setup.server_source)

        if not self.prj.has_ssp():
            logger.warning("Unable to retrieve a synthetic cast > Continue the loop")
            return False

        # apply tss (if required)
        if self.prj.setup.server_apply_surface_sound_speed and self.cur_tss and self.cur_draft:
            self.prj.add_cur_tss(server_mode=True)

        logger.debug('Retrieved a new synthetic profile')
        return True

    def _transmit_profile(self) -> None:

        self.prj.setup.client_list.transmit_ssp(prj=self.prj, server_mode=True)

        if self.cur_tss:
            self.last_tx_tss = self.cur_tss
        self.last_lat_idx = self.cur_lat_idx
        self.last_lon_idx = self.cur_lon_idx

        if not self.prj.store_data():
            logger.warning("Unable to save to db!")

    def stop(self) -> None:
        self.shutdown.set()
