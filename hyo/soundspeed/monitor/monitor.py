from threading import Timer, Lock
import math
import os
import datetime
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.monitor.db import MonitorDb
from hyo.soundspeed.base.helper import explore_folder
from hyo.soundspeed.base.gdal_aux import GdalAux


class SurveyDataMonitor:

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
        self.base_name = None

    @property
    def output_folder(self):
        out_folder = os.path.join(self._prj.data_folder, "monitor")
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        return out_folder

    def open_output_folder(self):
        explore_folder(self.output_folder)

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

        db = MonitorDb(projects_folder=self.output_folder, base_name=self.base_name)
        db.add_point(timestamp=timestamp, lat=latitude, long=longitude, tss=tss, draft=draft, avg_depth=depth)

        self._lock.acquire()

        insert_idx = self.find_next_idx_in_time(timestamp)
        self._times.insert(insert_idx, timestamp)
        self._lats.insert(insert_idx, latitude)
        self._longs.insert(insert_idx, longitude)
        self._tsss.insert(insert_idx, tss)
        self._drafts.insert(insert_idx, draft)
        self._depths.insert(insert_idx, depth)

        self._lock.release()

        return msg

    def find_next_idx_in_time(self, ts):
        time_idx = len(self._times)
        for _idx, _time in enumerate(self._times):
            if ts < _time:
                return _idx
        return time_idx

    def start_monitor(self, clear_data=True):
        if self._pause:
            logger.debug("resume monitoring")
            self._pause = False
            return

        if clear_data:
            self.clear_data()
            self.base_name = self._prj.current_project + "_" + datetime.datetime.now().strftime("%d%m%Y_%H%M%S")

        else:
            if self.base_name is None:
                self.base_name = self._prj.current_project + "_" + datetime.datetime.now().strftime("%d%m%Y_%H%M%S")

        self._active = True
        self._pause = False
        logger.debug("start monitoring")

        self.monitoring()

    def clear_data(self):
        self._times.clear()
        self._lats.clear()
        self._longs.clear()
        self._tsss.clear()
        self._drafts.clear()
        self._depths.clear()
        self._counter = 0
        self.base_name = None

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

    def add_db_data(self, filenames):

        for filename in filenames:

            if not os.path.exists(filename):
                raise RuntimeError("The passed db to merge does not exist")

            output_folder = os.path.abspath(os.path.dirname(filename))
            basename = os.path.splitext(os.path.basename(filename))[0]
            logger.debug("db: %s, %s" % (output_folder, basename))

            if self.base_name is None:
                self.base_name = basename

            load_in_db = True

            if (output_folder == self.output_folder) and (basename == self.base_name):
                logger.debug("Input and output are the same! -> Just loading data")
                load_in_db = False
            # print(output_folder, self.output_folder, basename, self.base_name)

            input_db = MonitorDb(projects_folder=output_folder, base_name=basename)
            # logger.debug("input db: %s" % input_db)

            if load_in_db:
                output_db = MonitorDb(projects_folder=self.output_folder, base_name=self.base_name)
                # logger.debug("output db: %s" % output_db)

            input_times, input_ids = input_db.timestamp_list()
            if len(input_times) == 0:
                logger.info("Input db is empty! -> Skipping db file")
                continue
            if load_in_db:
                output_times, output_ids = output_db.timestamp_list()
            else:
                output_times = list()

            for idx, input_time in enumerate(input_times):

                if input_time in output_times:
                    logger.debug("An entry with the same timestamp is in the output db! -> Skipping entry import")
                    continue

                timestamp, long, lat, tss, draft, avg_depth = input_db.point_by_id(input_ids[idx])
                if load_in_db:
                    success = output_db.add_point(timestamp=timestamp, lat=lat, long=long, tss=tss,
                                                  draft=draft, avg_depth=avg_depth)
                    if not success:
                        logger.warning("issue in importing point with timestamp: %s" % input_time)

                # insert the new data in cronological order
                self._lock.acquire()

                insert_idx = self.find_next_idx_in_time(input_time)
                self._times.insert(insert_idx, timestamp)
                self._lats.insert(insert_idx, lat)
                self._longs.insert(insert_idx, long)
                self._tsss.insert(insert_idx, tss)
                self._drafts.insert(insert_idx, draft)
                self._depths.insert(insert_idx, avg_depth)

                self._lock.release()

    def export_surface_speed_points_shapefile(self):
        db = MonitorDb(projects_folder=self.output_folder, base_name=self.base_name)
        db.export.export_surface_speed_points(output_folder=self.output_folder)

    def export_surface_speed_points_kml(self):
        db = MonitorDb(projects_folder=self.output_folder, base_name=self.base_name)
        db.export.export_surface_speed_points(output_folder=self.output_folder,
                                              ogr_format=GdalAux.ogr_formats['KML'])

    def export_surface_speed_points_csv(self):
        db = MonitorDb(projects_folder=self.output_folder, base_name=self.base_name)
        db.export.export_surface_speed_points(output_folder=self.output_folder,
                                              ogr_format=GdalAux.ogr_formats['CSV'])
