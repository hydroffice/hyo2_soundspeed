from threading import Timer, Lock
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

        self._times = list()
        self._lats = list()
        self._longs = list()
        self._tsss = list()
        self._drafts = list()
        self._depths = list()

        self._lock = Lock()
        self._external_lock = False

    def lock_data(self):
        self._lock.acquire()
        self._external_lock = True

    def unlock_data(self):
        self._lock.release()
        self._external_lock = False

    @property
    def times(self):
        if not self._external_lock:
            raise RuntimeError("Accessing resources without locking them!")
        return self._times

    @property
    def lats(self):
        if not self._external_lock:
            raise RuntimeError("Accessing resources without locking them!")
        return self._lats

    @property
    def longs(self):
        if not self._external_lock:
            raise RuntimeError("Accessing resources without locking them!")
        return self._longs

    @property
    def tsss(self):
        if not self._external_lock:
            raise RuntimeError("Accessing resources without locking them!")
        return self._tsss

    @property
    def drafts(self):
        if not self._external_lock:
            raise RuntimeError("Accessing resources without locking them!")
        return self._drafts

    @property
    def depths(self):
        if not self._external_lock:
            raise RuntimeError("Accessing resources without locking them!")
        return self._depths

    @property
    def active(self):
        return self._active

    def monitoring(self):
        if not self._active:
            # TODO: store the data on database
            self._times.clear()
            self._lats.clear()
            self._longs.clear()
            self._tsss.clear()
            self._drafts.clear()
            self._depths.clear()
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
        timestamp = self._prj.listeners.sis.xyz88.dg_time
        self._last_dgtime = timestamp
        msg += "%s, " % timestamp.strftime("%H:%M:%S.%f")

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
        tss = self._prj.listeners.sis.xyz88.sound_speed
        msg += '%.2f m/s,  ' % tss
        # - draft
        draft = self._prj.listeners.sis.xyz88.transducer_draft
        msg += '%.1f m, ' % draft
        # - mean depth
        depth = self._prj.listeners.sis.xyz88.mean_depth
        msg += '%.1f m' % depth

        self._lock.acquire()
        self._times.append(timestamp)
        self._lats.append(latitude)
        self._longs.append(longitude)
        self._tsss.append(tss)
        self._drafts.append(draft)
        self._depths.append(depth)
        self._lock.release()

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

    def nr_of_samples(self):
        self._lock.acquire()
        nr = len(self._times)
        self._lock.release()
        return nr
