from __future__ import absolute_import, division, print_function, unicode_literals

import os
import math
import csv
import numpy as np
from netCDF4 import Dataset
import logging
from datetime import datetime as dt, date

logger = logging.getLogger(__name__)

from ..abstract import AbstractAtlas
from ..ftp import Ftp
from ...profile.profile import Profile
from ...profile.profilelist import ProfileList
from ...profile.dicts import Dicts


class Woa13(AbstractAtlas):
    """WOA13 atlas"""

    def __init__(self, data_folder, prj):
        super(Woa13, self).__init__(data_folder=data_folder, prj=prj)
        self.name = self.__class__.__name__
        self.desc = "World Ocean Atlas 2013 v2"
        self.has_data_loaded = False
        self.search_radius = 2  # How far are we willing to look for solutions?

        self.t = list()
        self.s = list()
        self.landsea = None

        self.lat = None
        self.lon = None
        self.lat_step = 0.25
        self.lon_step = 0.25
        self.num_levels = None

        self.month_idx = 0
        self.season_idx = 0

    def is_present(self):
        """check the presence of one of the dataset file"""
        check_woa13_file = os.path.join(self.folder, 'temp', 'woa13_decav_t00_04v2.nc')
        if not os.path.exists(check_woa13_file):
            return False
        check_woa13_file = os.path.join(self.folder, 'sal', 'woa13_decav_s00_04v2.nc')
        if not os.path.exists(check_woa13_file):
            return False
        return True

    def download_db(self):
        """try to download the data set"""
        logger.debug('downloading WOA13 atlas')

        try:
            # remove all the content
            for root, dirs, files in os.walk(self.folder, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        except Exception as e:
            logger.error('during cleaning target folder: %s' % e)
            return False

        try:
            ftp = Ftp("ftp.ccom.unh.edu", show_progress=True, debug_mode=False,
                      progress=self.prj.progress)
            data_zip_src = "fromccom/hydroffice/woa13_temp.red.zip"
            data_zip_dst = os.path.join(self.data_folder, "woa13_temp.red.zip")
            ftp.get_file(data_zip_src, data_zip_dst, unzip_it=True)

            ftp = Ftp("ftp.ccom.unh.edu", show_progress=True, debug_mode=False,
                      progress=self.prj.progress)
            data_zip_src = "fromccom/hydroffice/woa13_sal.red.zip"
            data_zip_dst = os.path.join(self.data_folder, "woa13_sal.red.zip")
            ftp.get_file(data_zip_src, data_zip_dst, unzip_it=True)

            return self.is_present()

        except Exception as e:
            logger.error('during WOA13 download and unzip: %s' % e)
            return False

    def load_grids(self):
        """Load atlas grids"""
        try:
            for i in range(17):
                t_path = os.path.join(self.folder, "temp", "woa13_decav_t%02d_04v2.nc" % i)
                self.t.append(Dataset(t_path))
                s_path = os.path.join(self.folder, "sal", "woa13_decav_s%02d_04v2.nc" % i)
                self.s.append(Dataset(s_path))

            self.lat = self.t[0].variables['lat'][:]
            lon = self.t[0].variables['lon'][:]
            self.lon = np.vstack((lon[lon.size // 2:], lon[:lon.size // 2]))
            csv_iter = csv.reader(open((os.path.join(self.folder, "landsea_04.msk"))))
            next(csv_iter)  # skip firs header row
            next(csv_iter)   # skip another header row
            landsea = np.asarray([float(data[2]) for data in csv_iter])
            # print(landsea.shape, lons.size, lats.size)
            self.landsea = landsea.reshape((self.lat.size, self.lon.size))
            # from matplotlib import pyplot
            # pyplot.imshow(self.landsea, origin='lower')
            # pyplot.show()

            # How many depth levels do we have?
            self.num_levels = self.t[0].variables['depth'].size

        except Exception as e:
            logger.error("issue in reading the netCDF data: %s" % e)
            return False

        return True

    def grid_coords(self, lat, lon):
        """This does a nearest neighbour lookup"""
        lat_idx = (np.abs(self.lat - lat)).argmin()
        lon_idx = (np.abs(self.lon - lon)).argmin()
        logger.debug("grid coords: %s %s" % (lat_idx, lon_idx))
        return lat_idx, lon_idx

    def get_depth(self, lat, lon):
        """This helper method retrieve the max valid depth based on location"""
        lat_idx, lon_idx = self.grid_coords(lat, lon)
        t_profile = self.t[0].variables['t_an'][0, :, lat_idx, lon_idx]
        index = 0
        for sample in range(t_profile.size):
            if t_profile[sample] != 9.96921E36:  # null value
                index = sample
        return self.t[0].variables['depth'][index]

    def calc_indices(self, month):
        """Calculate the month index based on the julian day"""
        self.month_idx = month + 1
        if month < 3:
            self.season_idx = 13
        elif (month >= 3) or (month < 6):
            self.season_idx = 14
        elif (month >= 6) or (month < 9):
            self.season_idx = 15
        else:
            self.season_idx = 16

        # logger.debug("indices: %s, %s" % (self.month_idx, self.season_idx))

    def query(self, lat, lon, datestamp=None):
        """Query WOA13 for passed location and timestamp"""
        if datestamp is None:
            datestamp = dt.utcnow()
        if isinstance(datestamp, dt):
            datestamp = datestamp.date()
        if not isinstance(datestamp, date):
            raise RuntimeError("invalid date passed: %s" % type(datestamp))
        logger.debug("query: %s @ (%.6f, %.6f)" % (datestamp, lon, lat))

        # check the inputs
        if (lat is None) or (lon is None) or (datestamp is None):
            logger.error("invalid query: %s @ (%.6f, %.6f)" % (datestamp.strftime("%Y%m%d"), lon, lat))
            return None

        self.prj.progress.start("Retrieve WOA13 data")

        if not self.has_data_loaded:
            if not self.load_grids():
                return None
        self.prj.progress.update(20)

        self.calc_indices(month=datestamp.month)

        # Find the nearest grid node
        lat_base_idx, lon_base_idx = self.grid_coords(lat=lat, lon=lon)
        lat_offsets = range(lat_base_idx - self.search_radius, lat_base_idx + self.search_radius + 1)
        lon_offsets = range(lon_base_idx - self.search_radius, lon_base_idx + self.search_radius + 1)

        self.prj.progress.update(40)

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

                if this_lon_index >= self.t[self.month_idx].variables['lon'].size:
                    this_lon_index -= self.t[self.month_idx].variables['lon'].size

                # Check to see if we're at sea or on land
                if self.landsea[this_lat_index][this_lon_index] == 1:
                    # logger.debug("at land: %s, %s" % (this_lat_index, this_lon_index))
                    # from matplotlib import pyplot
                    # pyplot.imshow(self.landsea, origin='lower')
                    # pyplot.scatter([this_lon_index], [this_lat_index], c='r', s=40)
                    # pyplot.show()
                    continue

                # calculate the distance to the grid node
                dist = self.g.distance(lon, lat, self.t[self.month_idx].variables['lon'][this_lon_index],
                                       self.t[self.month_idx].variables['lat'][this_lat_index])

                # Keep track of the closest valid grid node to report the pseudo-cast position
                if dist < min_dist:
                    min_dist = dist
                    lat_idx = this_lat_index
                    lon_idx = this_lon_index

                # Extract monthly temperature and salinity profile for this location
                t_profile = self.t[self.month_idx].variables['t_an'][0, :, this_lat_index, this_lon_index]
                s_profile = self.s[self.month_idx].variables['s_an'][0, :, this_lat_index, this_lon_index]
                # Extract seasonal temperature and salinity profile for this location
                t_profile2 = self.t[self.season_idx].variables['t_an'][0, :, this_lat_index, this_lon_index]
                s_profile2 = self.s[self.season_idx].variables['s_an'][0, :, this_lat_index, this_lon_index]

                # Now do the same for the standard deviation profiles
                t_sd_profile = self.t[self.month_idx].variables['t_sd'][0, :, this_lat_index, this_lon_index]
                s_sd_profile = self.s[self.month_idx].variables['s_sd'][0, :, this_lat_index, this_lon_index]
                t_sd_profile2 = self.t[self.season_idx].variables['t_sd'][0, :, this_lat_index, this_lon_index]
                s_sd_profile2 = self.s[self.season_idx].variables['s_sd'][0, :, this_lat_index, this_lon_index]

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

        # logger.debug("visited: %s" % num_visited)
        self.prj.progress.update(90)

        if (lat_idx == -1) and (lon_idx == -1):
            logger.info("possible request on land")
            self.prj.progress.end()
            return None

        lat_out = self.t[self.month_idx].variables['lat'][lat_idx]
        lon_out = self.t[self.month_idx].variables['lon'][lon_idx]
        valid = dist_arr != 99999999
        num_values = t[valid].size

        # populate output profiles
        ssp = Profile()
        ssp.meta.sensor_type = Dicts.sensor_types['Synthetic']
        ssp.meta.probe_type = Dicts.probe_types['WOA13']
        ssp.meta.latitude = lat_out
        ssp.meta.longitude = lon_out
        ssp.meta.utc_time = dt(year=datestamp.year, month=datestamp.month, day=datestamp.day)
        ssp.init_data(num_values)
        ssp.data.depth = self.t[self.season_idx].variables['depth'][0:num_values]
        ssp.data.temp = t[valid]
        ssp.data.sal = s[valid]
        ssp.calc_speed()
        ssp.clone_data_to_proc()

        # - min/max
        # Isolate realistic values
        for i in range(t_min.size):
            if dist_t_sd[i] == 99999999 or dist_s_sd[i] == 99999999:
                num_values = i
                break
        # -- min
        ssp_min = Profile()
        ssp_min.meta.sensor_type = Dicts.sensor_types['Synthetic']
        ssp_min.meta.probe_type = Dicts.probe_types['WOA13']
        ssp_min.meta.latitude = lat_out
        ssp_min.meta.longitude = lon_out
        ssp_min.meta.utc_time = dt(year=datestamp.year, month=datestamp.month, day=datestamp.day)
        if num_values > 0:
            ssp_min.init_data(num_values)
            ssp_min.data.depth = self.t[self.season_idx].variables['depth'][0:num_values]
            ssp_min.data.temp = t_min[valid]
            ssp_min.data.sal = s_min[valid]
            ssp_min.calc_speed()
            ssp_min.clone_data_to_proc()
        else:
            ssp_min = None
        # -- max
        ssp_max = Profile()
        ssp_max.meta.sensor_type = Dicts.sensor_types['Synthetic']
        ssp_max.meta.probe_type = Dicts.probe_types['WOA13']
        ssp_max.meta.latitude = lat_out
        ssp_max.meta.longitude = lon_out
        ssp_max.meta.utc_time = dt(year=datestamp.year, month=datestamp.month, day=datestamp.day)
        ssp.meta.original_path = "WOA13_%s" % datestamp.strftime("%Y%m%d")
        if num_values > 0:
            ssp_max.init_data(num_values)
            ssp_max.data.depth = self.t[self.season_idx].variables['depth'][0:num_values]
            ssp_max.data.temp = t_max[valid]
            ssp_max.data.sal = s_max[valid]
            ssp_max.calc_speed()
            ssp_max.clone_data_to_proc()
        else:
            ssp_max = None

        profiles = ProfileList()
        profiles.append_profile(ssp)
        if ssp_min:
            profiles.append_profile(ssp_min)
        if ssp_max:
            profiles.append_profile(ssp_max)
        profiles.current_index = 0

        self.prj.progress.end()
        return profiles

    def clear_data(self):
        """Delete the data and reset the last loaded day"""
        logger.debug("clearing data")
        if self.has_data_loaded:
            # delete all the netcdf datasets
            for i in range(len(self.t)):
                if self.t[i]:
                    self.t[i].close()
            self.t = list()
            for i in range(len(self.s)):
                if self.s[i]:
                    self.s[i].close()
            self.s = list()
            self.landsea = None
            self.lat = None
            self.lon = None
            self.lat_step = None
            self.lon_step = None
            self.num_levels = None
            self.month_idx = 0
            self.season_idx = 0
        self.has_data_loaded = False

    # --- repr

    def __repr__(self):
        msg = "%s" % super(Woa13, self).__repr__()
        return msg
