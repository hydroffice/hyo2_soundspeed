from threading import Timer
import math
import logging

logger = logging.getLogger(__name__)


class SoundSpeedMonitor:

    def __init__(self, prj, timing=3.0):
        logger.debug("Init sound speed monitor")
        self._prj = prj
        self._timing = timing

        self._active = False
        self._pause = False

        self._counter = 0
        self._last_dgtime = None

    @property
    def active(self):
        return self._active

    def monitoring(self):
        if not self._active:
            return

        if self._pause:
            logger.debug("pause")
            Timer(self._timing, self.monitoring).start()
            return

        msg = self._retrieve_from_sis()

        if len(msg) > 0:
            if (self._counter % 1) == 0:
                logger.debug("#%04d: monitor: %s" % (self._counter, msg))
            self._counter += 1
        Timer(self._timing, self.monitoring).start()

    def _retrieve_from_sis(self):

        msg = str()

        # be sure that we have both navigation and depth datagrams
        if self._prj.listeners.sis.nav is None:
            return str()
        if self._prj.listeners.sis.nav.dg_time is None:
            return str()
        if (self._prj.listeners.sis.nav.latitude is None) or (self._prj.listeners.sis.nav.longitude is None):
            return str()
        if self._prj.listeners.sis.xyz88 is None:
            return str()
        if self._prj.listeners.sis.xyz88.sound_speed is None:
            return str()

        # time stamp
        # - check to avoid to store the latest datagram after SIS is turned off
        if self._last_dgtime:
            if self._last_dgtime >= self._prj.listeners.sis.xyz88.dg_time:
                return str()
        # - add string
        msg += "%s, " % (self._prj.listeners.sis.xyz88.dg_time.strftime("%H:%M:%S.%f"))
        self._last_dgtime = self._prj.listeners.sis.xyz88.dg_time

        # position
        # - latitude
        latitude = self._prj.listeners.sis.nav.latitude
        if latitude >= 0:
            letter = "N"
        else:
            letter = "S"
        lat_min = float(60 * math.fabs(latitude - int(latitude)))
        lat_str = "%02d\N{DEGREE SIGN}%7.3f'%s" % (int(math.fabs(latitude)), lat_min, letter)
        # - longitude
        longitude = self._prj.listeners.sis.nav.longitude
        if longitude < 0:
            letter = "W"
        else:
            letter = "E"
        lon_min = float(60 * math.fabs(longitude - int(longitude)))
        lon_str = "%03d\N{DEGREE SIGN}%7.3f'%s" % (int(math.fabs(longitude)), lon_min, letter)
        # - add string
        msg += "(%s, %s), " % (lat_str, lon_str)

        # - tss
        msg += '%.2f m/s,  ' % self._prj.listeners.sis.xyz88.sound_speed
        # - draft
        msg += '%.1f m, ' % self._prj.listeners.sis.xyz88.transducer_draft
        # - mean depth
        msg += '%.1f m' % self._prj.listeners.sis.xyz88.mean_depth

        return msg

    def start_monitor(self):
        if self._pause:
            logger.debug("resume monitoring")
            self._pause = False
            return

        self._active = True
        self._pause = False
        self._counter = 0
        logger.debug("start monitoring")

        self.monitoring()

    def pause_monitor(self):
        self._active = True
        self._pause = True
        logger.debug("pause monitoring")

    def stop_monitor(self):
        self._active = False
        self._pause = False
        logger.debug("stop monitoring")
