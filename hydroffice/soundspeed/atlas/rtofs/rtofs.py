from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime as dt, date, timedelta
from netCDF4 import Dataset
import numpy as np
import httplib
from urlparse import urlparse
import logging

logger = logging.getLogger(__name__)

from ..abstract import AbstractAtlas
from ...profile.profile import Profile
from ...profile.profilelist import ProfileList
from ...profile.dicts import Dicts
from ...profile.oceanography import Oceanography as Oc


class Rtofs(AbstractAtlas):
    """RTOFS atlas"""

    def __init__(self, data_folder, prj):
        super(Rtofs, self).__init__(data_folder=data_folder, prj=prj)
        self.name = self.__class__.__name__
        self.desc = "Global Real-Time Ocean Forecast System"

        # How far are we willing to look for solutions? size in grid nodes
        self.search_window = 5
        self.search_half_window = self.search_window // 2
        # 2000 dDar is the ref depth associated with the potential temperatures in the grid (sigma-2)
        self.ref_p = 2000

        self.has_data_loaded = False  # grids are "loaded" ? (netCDF files are opened)
        self.last_loaded_day = date(1900, 1, 1)  # some silly day in the past
        self.file_temp = None
        self.file_sal = None
        self.day_idx = None
        self.d = None
        self.lat = None
        self.lon = None
        self.lat_step = None
        self.lat_0 = None
        self.lon_step = None
        self.lon_0 = None

    def is_present(self):
        """check the availability"""
        return self.has_data_loaded

    def download_db(self, datestamp=None, server_mode=False):
        """try to connect and load info from the data set"""
        if datestamp is None:
            datestamp = dt.utcnow()
        if isinstance(datestamp, dt):
            datestamp = datestamp.date()
        if not isinstance(datestamp, date):
            raise RuntimeError("invalid date passed: %s" % type(datestamp))

        if not self.download_files(datestamp=datestamp, server_mode=server_mode):
            return False

        try:
            # Now get latitudes, longitudes and depths for x,y,z referencing
            self.d = self.file_temp.variables['lev'][:]
            self.lat = self.file_temp.variables['lat'][:]
            self.lon = self.file_temp.variables['lon'][:]
            # logger.debug('d:(%s)\n%s' % (self.d.shape, self.d))
            # logger.debug('lat:(%s)\n%s' % (self.lat.shape, self.lat))
            # logger.debug('lon:(%s)\n%s' % (self.lon.shape, self.lon))

        except Exception as e:
            logger.error("troubles in variable lookup for lat/long grid and/or depth: %s" % e)
            self.clear_data()
            return False

        self.lat_0 = self.lat[0]
        self.lat_step = self.lat[1] - self.lat_0
        self.lon_0 = self.lon[0]
        self.lon_step = self.lon[1] - self.lon_0

        # logger.debug("0(%.3f, %.3f); step(%.3f, %.3f)" % (self.lat_0, self.lon_0, self.lat_step, self.lon_step))
        return True

    @staticmethod
    def check_url(url):
        p = urlparse(url)
        conn = httplib.HTTPConnection(p.netloc)
        conn.request('HEAD', p.path)
        resp = conn.getresponse()
        return resp.status < 400

    @staticmethod
    def build_check_urls(input_date):
        """make up the url to use for salinity and temperature"""
        # Primary server: http://nomads.ncep.noaa.gov/pub/data/nccf/com/rtofs/prod/rtofs.20160410/
        url_temp = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/rtofs/prod/rtofs.%s/rtofs_glo_3dz_n024_daily_3ztio.nc' \
                   % input_date.strftime("%Y%m%d")
        url_sal = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/rtofs/prod/rtofs.%s/rtofs_glo_3dz_n024_daily_3zsio.nc' \
                  % input_date.strftime("%Y%m%d")
        return url_temp, url_sal

    @staticmethod
    def build_opendap_urls(input_date):
        """make up the url to use for salinity and temperature"""
        # Primary server: http://nomads.ncep.noaa.gov:9090/dods/rtofs
        url_temp = 'http://nomads.ncep.noaa.gov:9090/dods/rtofs/rtofs_global%s/rtofs_glo_3dz_nowcast_daily_temp' \
                   % input_date.strftime("%Y%m%d")
        url_sal = 'http://nomads.ncep.noaa.gov:9090/dods/rtofs/rtofs_global%s/rtofs_glo_3dz_nowcast_daily_salt' \
                  % input_date.strftime("%Y%m%d")
        return url_temp, url_sal

    def download_files(self, datestamp, server_mode=False):
        """Actually, just try to connect with the remote files

        For a given queried date, we may have to use the forecast from the previous
        day since the current nowcast doesn't hold data for today (solved?)
        """
        if not isinstance(datestamp, date):
            raise RuntimeError("invalid date passed: %s" % type(datestamp))

        # check if the files are loaded and that the date matches
        if self.has_data_loaded:
            # logger.info("%s" % self.last_loaded_day)
            if self.last_loaded_day == datestamp:
                return True
            else:  # the data are old
                logger.info("cleaning data: %s %s" % (self.last_loaded_day, datestamp))
                self.clear_data()

        self.prj.progress.start("Download RTOFS", server_mode=server_mode)

        url_ck_temp, url_ck_sal = self.build_check_urls(datestamp)
        if not (self.check_url(url_ck_temp) and self.check_url(url_ck_sal)):
            datestamp -= timedelta(days=1)
        url_temp, url_sal = self.build_opendap_urls(datestamp)

        self.prj.progress.update(30)
        logger.debug('downloading RTOFS data for %s' % datestamp)

        try:
            # Try out today's grids
            self.file_temp = Dataset(url_temp)
            self.prj.progress.update(60)
            self.file_sal = Dataset(url_sal)
            self.prj.progress.update(80)
            self.day_idx = 2  # usually 3 1-day steps
        except RuntimeError:
            logger.warning("unable to access data: %s" % datestamp.strftime("%Y%m%d"))
            self.clear_data()
            self.prj.progress.end()
            return False

        self.has_data_loaded = True
        self.last_loaded_day = datestamp
        logger.info("loaded data for %s" % datestamp)
        self.prj.progress.end()
        return True

    def grid_coords(self, lat, lon, datestamp, server_mode=False):
        """Convert the passed position in RTOFS grid coords"""

        # check if we need to update the data set (new day!)
        if not self.download_db(datestamp, server_mode=server_mode):
            logger.error("troubles in updating data set for timestamp: %s"
                         % datestamp.strftime("%Y%m%d"))
            raise RuntimeError('troubles in db download')

        # make longitude "safe" since RTOFS grid starts at east longitude 70-ish degrees
        if lon < self.lon_0:
            lon += 360.0

        # This does a nearest neighbour lookup
        lat_idx = int(round((lat - self.lat_0) / self.lat_step, 0))
        lon_idx = int(round((lon - self.lon_0) / self.lon_step, 0))

        return lat_idx, lon_idx

    def query(self, lat, lon, datestamp=None, server_mode=False):
        """Query RTOFS for passed location and timestamp"""
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

        try:
            lat_idx, lon_idx = self.grid_coords(lat, lon, datestamp=datestamp, server_mode=server_mode)
        except TypeError as e:
            logger.critical("while converting location to grid coords, %s" % e)
            return None

        # logger.debug("idx > lat: %s, lon: %s" % (lat_idx, lon_idx))
        lat_s_idx = lat_idx - self.search_half_window
        lat_n_idx = lat_idx + self.search_half_window
        lon_w_idx = lon_idx - self.search_half_window
        lon_e_idx = lon_idx + self.search_half_window
        # logger.info("indices -> %s %s %s %s" % (lat_s_idx, lat_n_idx, lon_w_idx, lon_e_idx))
        if lon < self.lon_0:  # Make all longitudes safe
            lon += 360.0

        self.prj.progress.start("Retrieve RTOFS data", server_mode=server_mode)

        longitudes = np.zeros((self.search_window, self.search_window))
        if (lon_e_idx < self.lon.size) and (lon_w_idx >= 0):
            # logger.info("safe case")

            # Need +1 on the north and east indices since it is the "stop" value in these slices
            t = self.file_temp.variables['temperature'][self.day_idx, :, lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]
            s = self.file_sal.variables['salinity'][self.day_idx, :, lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]
            # Set 'unfilled' elements to NANs (BUT when the entire array has valid data, it returns numpy.ndarray)
            if isinstance(t, np.ma.core.MaskedArray):
                t_mask = t.mask
                t[t_mask] = np.nan
            if isinstance(s, np.ma.core.MaskedArray):
                s_mask = s.mask
                s[s_mask] = np.nan

            lons = self.lon[lon_w_idx:lon_e_idx + 1]
            for i in range(self.search_window):
                longitudes[i, :] = lons
        else:
            logger.info("split case")

            # --- Do the left portion of the array first, this will run into the wrap longitude
            lon_e_idx = self.lon.size - 1
            # lon_west_index can be negative if lon_index is on the westernmost end of the array
            if lon_w_idx < 0:
                lon_w_idx = lon_w_idx + self.lon.size
            # logger.info("using lon west/east indices -> %s %s" % (lon_w_idx, lon_e_idx))

            # Need +1 on the north and east indices since it is the "stop" value in these slices
            t_left = self.file_temp.variables['temperature'][self.day_idx, :, lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]
            s_left = self.file_sal.variables['salinity'][self.day_idx, :, lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]
            # Set 'unfilled' elements to NANs (BUT when the entire array has valid data, it returns numpy.ndarray)
            if isinstance(t_left, np.ma.core.MaskedArray):
                t_mask = t_left.mask
                t_left[t_mask] = np.nan
            if isinstance(s_left, np.ma.core.MaskedArray):
                s_mask = s_left.mask
                s_left[s_mask] = np.nan

            lons_left = self.lon[lon_w_idx:lon_e_idx + 1]
            for i in range(self.search_window):
                longitudes[i, 0:lons_left.size] = lons_left
            # logger.info("longitudes are now: %s" % longitudes)

            # --- Do the right portion of the array first, this will run into the wrap
            # longitude so limit it accordingly
            lon_w_idx = 0
            lon_e_idx = self.search_window - lons_left.size - 1

            # Need +1 on the north and east indices since it is the "stop" value in these slices
            t_right = self.file_temp.variables['temperature'][self.day_idx, :, lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]
            s_right = self.file_sal.variables['salinity'][self.day_idx, :, lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]
            # Set 'unfilled' elements to NANs (BUT when the entire array has valid data, it returns numpy.ndarray)
            if isinstance(t_right, np.ma.core.MaskedArray):
                t_mask = t_right.mask
                t_right[t_mask] = np.nan
            if isinstance(s_right, np.ma.core.MaskedArray):
                s_mask = s_right.mask
                s_right[s_mask] = np.nan

            lons_right = self.lon[lon_w_idx:lon_e_idx + 1]
            for i in range(self.search_window):
                longitudes[i, lons_left.size:self.search_window] = lons_right

            # merge data
            t = np.zeros((self.file_temp.variables['lev'].size, self.search_window, self.search_window))
            t[:, :, 0:lons_left.size] = t_left
            t[:, :, lons_left.size:self.search_window] = t_right
            s = np.zeros((self.file_temp.variables['lev'].size, self.search_window, self.search_window))
            s[:, :, 0:lons_left.size] = s_left
            s[:, :, lons_left.size:self.search_window] = s_right

        # logger.info("done data retrieval > calculating nodes distance")
        self.prj.progress.update(40)

        # Calculate distances from requested position to each of the grid node locations
        distances = np.zeros((self.d.size, self.search_window, self.search_window))
        latitudes = np.zeros((self.search_window, self.search_window))
        lats = self.lat[lat_s_idx:lat_n_idx + 1]
        for i in range(self.search_window):
            latitudes[:, i] = lats
        for i in range(self.search_window):
            for j in range(self.search_window):
                dist = self.g.distance(longitudes[i, j], latitudes[i, j], lon, lat)
                distances[:, i, j] = dist
                # logger.info("node %s, pos: %3.1f, %3.1f, dist: %3.1f"
                #             % (i, latitudes[i, j], longitudes[i, j], distances[0, i, j]))
        # logger.info("distance array:\n%s" % distances[0])
        # Get mask of "no data" elements and replace these with NaNs in distance array
        t_mask = np.isnan(t)
        distances[t_mask] = np.nan
        s_mask = np.isnan(s)
        distances[s_mask] = np.nan

        self.prj.progress.update(70)

        # Spin through all the depth levels
        temp_pot = np.zeros(self.d.size)
        temp_in_situ = np.zeros(self.d.size)
        d = np.zeros(self.d.size)
        sal = np.zeros(self.d.size)
        num_values = 0
        for i in range(self.d.size):
            t_level = t[i]
            s_level = s[i]
            d_level = distances[i]

            try:
                ind = np.nanargmin(d_level)
            except ValueError:
                # logger.info("%s: all-NaN slices" % i)
                continue

            if np.isnan(ind):
                logger.info("%s: bottom of valid data" % i)
                break

            ind2 = np.unravel_index(ind, t_level.shape)

            t_closest = t_level[ind2]
            s_closest = s_level[ind2]
            d_closest = d_level[ind2]

            temp_pot[i] = t_closest
            sal[i] = s_closest
            d[i] = self.d[i]

            # Calculate in-situ temperature
            p = Oc.d2p(d[i], lat)
            temp_in_situ[i] = Oc.in_situ_temp(s=sal[i], t=t_closest, p=p, pr=self.ref_p)
            # logger.info("%02d: %6.1f %6.1f > T/S/Dist: %3.1f %3.1f %3.1f [pot.temp. %3.1f]"
            #             % (i, d[i], p, temp_in_situ[i], s_closest, d_closest, t_closest))

            num_values += 1

        if num_values == 0:
            logger.info("no data from lookup!")
            self.prj.progress.end()
            return None

        ind = np.nanargmin(distances[0])
        ind2 = np.unravel_index(ind, distances[0].shape)
        lat_out = latitudes[ind2]
        lon_out = longitudes[ind2]
        while lon_out > 180.0:
            lon_out -= 360.0

        self.prj.progress.update(90)

        # Make a new SV object to return our query in
        ssp = Profile()
        ssp.meta.sensor_type = Dicts.sensor_types['Synthetic']
        ssp.meta.probe_type = Dicts.probe_types['RTOFS']
        ssp.meta.latitude = lat_out
        ssp.meta.longitude = lon_out
        ssp.meta.utc_time = dt(year=datestamp.year, month=datestamp.month, day=datestamp.day)
        ssp.meta.original_path = "RTOFS_%s" % datestamp.strftime("%Y%m%d")
        ssp.init_data(num_values)
        ssp.data.depth = d[0:num_values]
        ssp.data.temp = temp_in_situ[0:num_values]
        ssp.data.sal = sal[0:num_values]
        ssp.calc_data_speed()
        ssp.clone_data_to_proc()
        ssp.init_sis()

        profiles = ProfileList()
        profiles.append_profile(ssp)

        self.prj.progress.end()
        return profiles

    def clear_data(self):
        """Delete the data and reset the last loaded day"""
        logger.debug("clearing data")
        if self.has_data_loaded:
            self.file_temp.close()
            self.file_temp = None
            self.file_sal.close()
            self.file_sal = None
            self.lat = None
            self.lon = None
            self.lat_step = None
            self.lat_0 = None
            self.lon_step = None
            self.lon_0 = None
        self.has_data_loaded = False  # grids are "loaded" ? (netCDF files are opened)
        self.last_loaded_day = date(1900, 1, 1)  # some silly day in the past
        self.day_idx = None

    def __repr__(self):
        msg = "%s" % super(Rtofs, self).__repr__()
        msg += "  <has data loaded: %s>\n" % self.has_data_loaded
        msg += "  <last loaded day: %s>\n" % self.last_loaded_day.strftime("%d\%m\%Y")
        return msg
