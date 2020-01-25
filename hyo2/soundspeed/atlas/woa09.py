import os
import math
import numpy as np
from netCDF4 import Dataset
import logging
from datetime import datetime as dt
from typing import Union

from hyo2.abc.lib.ftp import Ftp

from hyo2.soundspeed.atlas.abstract import AbstractAtlas
from hyo2.soundspeed.profile.profile import Profile
from hyo2.soundspeed.profile.profilelist import ProfileList
from hyo2.soundspeed.profile.dicts import Dicts

logger = logging.getLogger(__name__)


class Woa09(AbstractAtlas):
    """WOA09 atlas"""

    def __init__(self, data_folder: str, prj: 'hyo2.soundspeed.soundspeed import SoundSpeedLibrary') -> None:
        super(Woa09, self).__init__(data_folder=data_folder, prj=prj)
        self.name = self.__class__.__name__
        self.desc = "World Ocean Atlas 2009"
        self.has_data_loaded = False
        self.search_radius = 2  # How far are we willing to look for solutions?

        self.t_annual = None
        self.t_monthly = None
        self.t_seasonal = None
        self.s_monthly = None
        self.s_seasonal = None
        self.landsea = None
        # self.basin = None

        self.lat_step = None
        self.lon_step = None
        self.lat_0 = None
        self.lon_0 = None
        self.num_levels = None

        self.month_idx = 0
        self.season_idx = 0

    def is_present(self) -> bool:
        """Check the presence of one of the db file

        The default location is first checked. If not present, the search is enlarged to past installations"""

        # first check the location based on the current version
        check_woa09_file = os.path.join(self.data_folder, 'landsea.msk')
        if os.path.exists(check_woa09_file):
            return True
        # logger.info('unable to locate the WOA09 db at the default location: %s' % self.folder)

        # no way to find the database
        logger.warning("unable to locate the WOA09 db")
        return False

    def download_db(self) -> bool:
        """try to download the data set"""
        logger.debug('downloading WOA9 atlas')

        # FIXME: this was too dangerous if the user select the wrong folder
        # try:
        #     # remove all the content
        #     for root, dirs, files in os.walk(self.data_folder, topdown=False):
        #         for name in files:
        #             os.remove(os.path.join(root, name))
        #         for name in dirs:
        #             os.rmdir(os.path.join(root, name))
        # except Exception as e:
        #     logger.error('during cleaning target folder: %s' % e)
        #     return False

        try:
            ftp = Ftp("ftp.ccom.unh.edu", show_progress=True, debug_mode=False,
                      progress=self.prj.progress)
            data_zip_src = "fromccom/hydroffice/woa09.red.zip"
            data_zip_dst = os.path.abspath(os.path.join(self.data_folder, os.pardir, "woa09.red.zip"))
            ftp.get_file(data_zip_src, data_zip_dst, unzip_it=True)
            ftp.disconnect()
            return self.is_present()

        except Exception as e:
            logger.error('during WOA09 download and unzip: %s' % e)
            return False

    def load_grids(self) -> bool:
        """Load atlas grids"""
        try:
            self.t_annual = Dataset(os.path.join(self.data_folder, "temperature_annual_1deg.nc"))
            self.t_monthly = Dataset(os.path.join(self.data_folder, "temperature_monthly_1deg.nc"))
            self.t_seasonal = Dataset(os.path.join(self.data_folder, "temperature_seasonal_1deg.nc"))
            self.s_monthly = Dataset(os.path.join(self.data_folder, "salinity_monthly_1deg.nc"))
            self.s_seasonal = Dataset(os.path.join(self.data_folder, "salinity_seasonal_1deg.nc"))
            landsea = np.genfromtxt((os.path.join(self.data_folder, "landsea.msk")))
            self.landsea = landsea.reshape((180, 360))
            # basin = np.genfromtxt((os.path.join(self.folder, "basin.msk")))
            # self.basin = basin.reshape((33, 180, 360))

        except Exception as e:
            logger.error("issue in reading the netCDF data: %s" % e)
            return False

        # What's our grid interval in lat/long
        self.lat_step = self.t_monthly.variables['lat'][1] - self.t_monthly.variables['lat'][0]
        self.lat_0 = self.t_monthly.variables['lat'][0]
        self.lon_step = self.t_monthly.variables['lon'][1] - self.t_monthly.variables['lon'][0]
        self.lon_0 = self.t_monthly.variables['lon'][0]
        # How many depth levels do we have?
        self.num_levels = self.t_seasonal.variables['depth'].size
        logger.debug("0(%.3f, %.3f); step(%.3f, %.3f); depths: %s"
                     % (self.lat_0, self.lon_0, self.lat_step, self.lon_step, self.num_levels))

        return True

    def get_depth(self, lat: float, lon: float) -> float:
        """This helper method retrieve the max valid depth based on location"""
        lat_idx, lon_idx = self.grid_coords(lat, lon)
        t_profile = self.t_annual.variables['t_an'][0, :, lat_idx, lon_idx]
        index = 0
        for sample in range(t_profile.size):
            if t_profile[sample] != 9.96921E36:  # null value
                index = sample
        return self.t_annual.variables['depth'][index]

    def calc_month_idx(self, jday: int) -> None:
        """Calculate the month index based on the julian day"""
        min_value = 367
        i = 0
        for d in self.t_monthly.variables['time'][:]:
            if math.fabs(d - jday) < min_value:
                min_value = math.fabs(d - jday)
                self.month_idx = int(i)
            i += 1

    def calc_season_idx(self, jday: int) -> None:
        """Calculate the season index based on the julian day"""
        min_value = 367
        i = 0
        for d in self.t_seasonal.variables['time'][:]:
            if math.fabs(d - jday) < min_value:
                min_value = math.fabs(d - jday)
                self.season_idx = int(i)
            i += 1

    def grid_coords(self, lat: float, lon: float) -> tuple:
        """This does a nearest neighbour lookup"""

        if not self.has_data_loaded:
            if not self.load_grids():
                raise RuntimeError('troubles in db load')

        lat_idx = int(round((lat - self.lat_0) / self.lat_step, 0))
        lon_idx = int(round((lon - self.lon_0) / self.lon_step, 0))
        return lat_idx, lon_idx

    def query(self, lat: float, lon: float, dtstamp: Union[dt, None] = None, server_mode: bool = False):
        """Query WOA09 for passed location and timestamp"""
        if dtstamp is None:
            dtstamp = dt.utcnow()
        if not isinstance(dtstamp, dt):
            raise RuntimeError("invalid datetime passed: %s" % type(dtstamp))
        logger.debug("query: %s @ (%.6f, %.6f)" % (dtstamp, lon, lat))

        # check the inputs
        if (lat is None) or (lon is None) or (dtstamp is None):
            logger.error("invalid query: %s @ (%s, %s)" % (dtstamp.strftime("%Y/%m/%d %H:%M:%S"), lon, lat))
            return None
        if lon < 0:  # Make all longitudes positive
            lon += 360.0

        if not self.has_data_loaded:
            if not self.load_grids():
                logger.error("No data")
                return None

        # calculate month and season indices (based on julian day)
        jd = int(dtstamp.strftime("%j"))
        self.calc_month_idx(jday=jd)
        self.calc_season_idx(jday=jd)

        # Find the nearest grid node
        lat_base_idx, lon_base_idx = self.grid_coords(lat, lon)
        lat_offsets = range(lat_base_idx - self.search_radius, lat_base_idx + self.search_radius + 1)
        lon_offsets = range(lon_base_idx - self.search_radius, lon_base_idx + self.search_radius + 1)

        # Search nodes surrounding the requested position to find the closest non-land
        t = np.zeros(self.num_levels)
        s = np.zeros(self.num_levels)
        t_min = np.zeros(self.num_levels)
        s_min = np.zeros(self.num_levels)
        t_max = np.zeros(self.num_levels)
        s_max = np.zeros(self.num_levels)
        dist_arr = np.zeros(self.num_levels)
        dist_t_sd = np.zeros(self.num_levels)
        dist_s_sd = np.zeros(self.num_levels)
        dist_arr[:] = 99999999
        dist_t_sd[:] = 99999999
        dist_s_sd[:] = 99999999
        min_dist = 999999999
        num_visited = 0
        # These keep track of the closest node found, this will also
        # be used to populate lat/lon of the cast to be delivered
        lat_idx = -1
        lon_idx = -1
        for this_lat_index in lat_offsets:
            for this_lon_index in lon_offsets:

                if this_lon_index >= self.t_monthly.variables['lon'].size:
                    this_lon_index -= self.t_monthly.variables['lon'].size

                # Check to see if we're at sea or on land
                if self.landsea[this_lat_index][this_lon_index] == 1:
                    # logger.debug("at land: %s, %s" % (this_lat_index, this_lon_index))
                    continue

                # calculate the distance to the grid node
                dist = self.g.distance(lon, lat, self.t_monthly.variables['lon'][this_lon_index],
                                       self.t_monthly.variables['lat'][this_lat_index])

                # Keep track of the closest valid grid node to report the pseudo-cast position
                if dist < min_dist:
                    min_dist = dist
                    lat_idx = this_lat_index
                    lon_idx = this_lon_index

                # Extract monthly temperature and salinity profile for this location
                t_profile = self.t_monthly.variables['t_an'][self.month_idx, :, this_lat_index, this_lon_index]
                s_profile = self.s_monthly.variables['s_an'][self.month_idx, :, this_lat_index, this_lon_index]
                # Extract seasonal temperature and salinity profile for this location
                t_profile2 = self.t_seasonal.variables['t_an'][self.season_idx, :, this_lat_index, this_lon_index]
                s_profile2 = self.s_seasonal.variables['s_an'][self.season_idx, :, this_lat_index, this_lon_index]

                # Now do the same for the standard deviation profiles
                t_sd_profile = self.t_monthly.variables['t_sd'][self.month_idx, :, this_lat_index, this_lon_index]
                s_sd_profile = self.s_monthly.variables['s_sd'][self.month_idx, :, this_lat_index, this_lon_index]
                t_sd_profile2 = self.t_seasonal.variables['t_sd'][self.season_idx, :, this_lat_index, this_lon_index]
                s_sd_profile2 = self.s_seasonal.variables['s_sd'][self.season_idx, :, this_lat_index, this_lon_index]

                # Overwrite the top of the seasonal profiles with the monthly profiles
                t_profile2[0:t_profile.size] = t_profile
                s_profile2[0:s_profile.size] = s_profile
                t_sd_profile2[0:t_sd_profile.size] = t_sd_profile
                s_sd_profile2[0:s_sd_profile.size] = s_sd_profile

                # For each element in the profile, only keep those whose distance is closer than values
                # found from previous iterations (maintain the closest value at each depth level)
                for i in range(t_profile2.size):
                    if (dist < dist_arr[i]) and (t_profile2[i] < 50.0) and \
                            (s_profile2[i] < 500.0) and (s_profile2[i] >= 0):
                        t[i] = t_profile2[i]
                        s[i] = s_profile2[i]
                        dist_arr[i] = dist

                # Now do the same thing for the temperature standard deviations
                for i in range(t_sd_profile2.size):
                    if (dist < dist_t_sd[i]) and (t_sd_profile2[i] < 50.0) and (t_sd_profile2[i] > -2):
                        t_min[i] = t_profile2[i] - t_sd_profile2[i]
                        if t_min[i] < -2.0:  # can't have overly cold water
                            t_min[i] = -2.0
                        t_max[i] = t_profile2[i] + t_sd_profile2[i]
                        dist_t_sd[i] = dist

                # Now do the same thing for the salinity standard deviations
                for i in range(s_sd_profile2.size):
                    if (dist < dist_s_sd[i]) and (s_sd_profile2[i] < 500.0) and (s_sd_profile2[i] >= 0):
                        s_min[i] = s_profile2[i] - s_sd_profile2[i]
                        if s_min[i] < 0:  # Can't have a negative salinity
                            s_min[i] = 0
                        s_max[i] = s_profile2[i] + s_sd_profile2[i]
                        dist_s_sd[i] = dist

                num_visited += 1

        logger.debug("visited: %s" % num_visited)

        if (lat_idx == -1) and (lon_idx == -1):
            logger.info("possible request on land")
            return None

        valid = dist_arr != 99999999
        num_values = t[valid].size

        if lon > 180.0:  # Go back to negative longitude
            lon -= 360.0

        # populate output profiles
        ssp = Profile()
        ssp.meta.sensor_type = Dicts.sensor_types['Synthetic']
        ssp.meta.probe_type = Dicts.probe_types['WOA09']
        ssp.meta.latitude = lat
        ssp.meta.longitude = lon
        ssp.meta.utc_time = dt(year=dtstamp.year, month=dtstamp.month, day=dtstamp.day,
                               hour=dtstamp.hour, minute=dtstamp.minute, second=dtstamp.second)
        ssp.meta.original_path = "WOA09_%s" % dtstamp.strftime("%Y%m%d_%H%M%S")
        ssp.init_data(num_values)
        ssp.data.depth = self.t_seasonal.variables['depth'][0:num_values]
        ssp.data.temp = t[valid]
        ssp.data.sal = s[valid]
        ssp.calc_data_speed()
        ssp.clone_data_to_proc()
        ssp.init_sis()

        # - min/max
        # Isolate realistic values
        for i in range(t_min.size):

            if dist_t_sd[i] == 99999999 or dist_s_sd[i] == 99999999:
                num_values = i
                break

        # -- min
        ssp_min = Profile()
        ssp_min.meta.sensor_type = Dicts.sensor_types['Synthetic']
        ssp_min.meta.probe_type = Dicts.probe_types['WOA09']
        ssp_min.meta.latitude = lat
        ssp_min.meta.longitude = lon
        ssp_min.meta.utc_time = dt(year=dtstamp.year, month=dtstamp.month, day=dtstamp.day,
                                   hour=dtstamp.hour, minute=dtstamp.minute, second=dtstamp.second)
        if num_values > 0:
            ssp_min.init_data(num_values)
            ssp_min.data.depth = self.t_seasonal.variables['depth'][0:num_values]
            ssp_min.data.temp = t_min[valid][0:num_values]
            ssp_min.data.sal = s_min[valid][0:num_values]
            ssp_min.calc_data_speed()
            ssp_min.clone_data_to_proc()
            ssp_min.init_sis()
        else:
            ssp_min = None

        # -- max
        ssp_max = Profile()
        ssp_max.meta.sensor_type = Dicts.sensor_types['Synthetic']
        ssp_max.meta.probe_type = Dicts.probe_types['WOA09']
        ssp_max.meta.latitude = lat
        ssp_max.meta.longitude = lon
        ssp_max.meta.utc_time = dt(year=dtstamp.year, month=dtstamp.month, day=dtstamp.day,
                                   hour=dtstamp.hour, minute=dtstamp.minute, second=dtstamp.second)
        if num_values > 0:
            ssp_max.init_data(num_values)
            ssp_max.data.depth = self.t_seasonal.variables['depth'][0:num_values].astype(np.float64)
            ssp_max.data.temp = t_max[valid][0:num_values]
            ssp_max.data.sal = s_max[valid][0:num_values]
            ssp_max.calc_data_speed()
            ssp_max.clone_data_to_proc()
            ssp_max.init_sis()
        else:
            ssp_max = None

        profiles = ProfileList()
        profiles.append_profile(ssp)
        if ssp_min:
            profiles.append_profile(ssp_min)
        if ssp_max:
            profiles.append_profile(ssp_max)
        profiles.current_index = 0

        return profiles

    def clear_data(self) -> None:
        """Delete the data and reset the last loaded day"""
        logger.debug("clearing data")
        if self.has_data_loaded:
            if self.t_annual:
                self.t_annual.close()
            self.t_annual = None
            if self.t_monthly:
                self.t_monthly.close()
            self.t_monthly = None
            if self.t_seasonal:
                self.t_seasonal.close()
            self.t_seasonal = None
            if self.s_monthly:
                self.s_monthly.close()
            self.s_monthly = None
            if self.s_seasonal:
                self.s_seasonal.close()
            self.s_seasonal = None
            self.landsea = None
            # self.basin = None
            self.lat_step = None
            self.lon_step = None
            self.lat_0 = None
            self.lon_0 = None
            self.num_levels = None
            self.month_idx = 0
            self.season_idx = 0
        self.has_data_loaded = False

    # --- repr

    def __repr__(self) -> str:
        msg = "%s" % super(Woa09, self).__repr__()
        return msg
