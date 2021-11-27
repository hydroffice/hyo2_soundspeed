from datetime import datetime as dt, date, timedelta
import logging
from typing import Optional, Union

from netCDF4 import Dataset
import numpy as np
import requests

from hyo2.abc.lib.progress.cli_progress import CliProgress

from hyo2.soundspeed.atlas.abstract import AbstractAtlas
from hyo2.soundspeed.profile.profile import Profile
from hyo2.soundspeed.profile.profilelist import ProfileList
from hyo2.soundspeed.profile.dicts import Dicts
from hyo2.soundspeed.profile.oceanography import Oceanography as Oc

logger = logging.getLogger(__name__)


class Rtofs(AbstractAtlas):
    """RTOFS atlas"""

    def __init__(self, data_folder: str, prj: 'hyo2.soundspeed.soundspeed import SoundSpeedLibrary') -> None:
        super(Rtofs, self).__init__(data_folder=data_folder, prj=prj)
        self.name = self.__class__.__name__
        self.desc = "Global Real-Time Ocean Forecast System"

        # How far are we willing to look for solutions? size in grid nodes
        self._search_window = 5
        self._search_half_window = self._search_window // 2
        # 2000 dBar is the ref depth associated with the potential temperatures in the grid (sigma-2)
        self._ref_p = 2000

        self._has_data_loaded = False  # grids are "loaded" ? (netCDF files are opened)
        self._last_loaded_day = dt(1900, 1, 1)  # some silly day in the past
        self._file_temp = None
        self._file_sal = None
        self._day_idx = None
        self._d = None
        self._lat = None
        self._lon = None
        self._lat_step = None
        self._lat_0 = None
        self._lon_step = None
        self._lon_0 = None

    # ### public API ###

    def is_present(self) -> bool:
        """check the availability"""
        return self._has_data_loaded

    def download_db(self, dtstamp: Union[dt, None] = None, server_mode: bool = False) -> bool:
        """try to connect and load info from the data set"""
        if dtstamp is None:
            dtstamp = dt.utcnow()
        if not isinstance(dtstamp, dt):
            raise RuntimeError("invalid datetime passed: %s" % type(dtstamp))

        if not self._download_files(datestamp=dtstamp, server_mode=server_mode):
            return False

        try:
            # Now get latitudes, longitudes and depths for x,y,z referencing
            self._d = self._file_temp.variables['lev'][:]
            self._lat = self._file_temp.variables['lat'][:]
            self._lon = self._file_temp.variables['lon'][:]
            # logger.debug('d:(%s)\n%s' % (self._d.shape, self._d))
            # logger.debug('lat:(%s)\n%s' % (self._lat.shape, self._lat))
            # logger.debug('lon:(%s)\n%s' % (self._lon.shape, self._lon))

        except Exception as e:
            logger.error("troubles in variable lookup for lat/long grid and/or depth: %s" % e)
            self.clear_data()
            return False

        self._lat_0 = self._lat[0]
        self._lat_step = self._lat[1] - self._lat_0
        self._lon_0 = self._lon[0]
        self._lon_step = self._lon[1] - self._lon_0
        # logger.debug("0(%.3f, %.3f); step(%.3f, %.3f)" % (self._lat_0, self._lon_0, self._lat_step, self._lon_step))

        return True

    def query(self, lat: Optional[float], lon: Optional[float], dtstamp: Optional[dt] = None,
              server_mode: bool = False):
        """Query RTOFS for passed location and timestamp"""
        if dtstamp is None:
            dtstamp = dt.utcnow()
        if not isinstance(dtstamp, dt):
            raise RuntimeError("invalid datetime passed: %s" % type(dtstamp))
        logger.debug("query: %s @ (%.6f, %.6f)" % (dtstamp, lon, lat))

        # check the inputs
        if (lat is None) or (lon is None):
            logger.error("invalid query: %s @ (%s, %s)" % (dtstamp.strftime("%Y/%m/%d %H:%M:%S"), lon, lat))
            return None

        try:
            lat_idx, lon_idx = self.grid_coords(lat, lon, dtstamp=dtstamp, server_mode=server_mode)
        except TypeError as e:
            logger.critical("while converting location to grid coords, %s" % e)
            return None
        # logger.debug("idx > lat: %s, lon: %s" % (lat_idx, lon_idx))

        lat_s_idx = lat_idx - self._search_half_window
        lat_n_idx = lat_idx + self._search_half_window
        lon_w_idx = lon_idx - self._search_half_window
        lon_e_idx = lon_idx + self._search_half_window
        # logger.info("indices -> %s %s %s %s" % (lat_s_idx, lat_n_idx, lon_w_idx, lon_e_idx))
        if lon < self._lon_0:  # Make all longitudes safe
            lon += 360.0

        longitudes = np.zeros((self._search_window, self._search_window))
        if (lon_e_idx < self._lon.size) and (lon_w_idx >= 0):
            # logger.info("safe case")

            # Need +1 on the north and east indices since it is the "stop" value in these slices
            t = self._file_temp.variables['temperature'][self._day_idx, :, lat_s_idx:lat_n_idx + 1,
                lon_w_idx:lon_e_idx + 1]
            s = self._file_sal.variables['salinity'][self._day_idx, :, lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]
            # Set 'unfilled' elements to NANs (BUT when the entire array has valid data, it returns numpy.ndarray)
            if isinstance(t, np.ma.core.MaskedArray):
                t_mask = t.mask
                t._sharedmask = False
                t[t_mask] = np.nan
            if isinstance(s, np.ma.core.MaskedArray):
                s_mask = s.mask
                s._sharedmask = False
                s[s_mask] = np.nan

            lons = self._lon[lon_w_idx:lon_e_idx + 1]
            for i in range(self._search_window):
                longitudes[i, :] = lons
        else:
            logger.info("split case")

            # --- Do the left portion of the array first, this will run into the wrap longitude
            lon_e_idx = self._lon.size - 1
            # lon_west_index can be negative if lon_index is on the westernmost end of the array
            if lon_w_idx < 0:
                lon_w_idx = lon_w_idx + self._lon.size
            # logger.info("using lon west/east indices -> %s %s" % (lon_w_idx, lon_e_idx))

            # Need +1 on the north and east indices since it is the "stop" value in these slices
            t_left = self._file_temp.variables['temperature'][self._day_idx, :, lat_s_idx:lat_n_idx + 1,
                     lon_w_idx:lon_e_idx + 1]
            s_left = self._file_sal.variables['salinity'][self._day_idx, :, lat_s_idx:lat_n_idx + 1,
                     lon_w_idx:lon_e_idx + 1]
            # Set 'unfilled' elements to NANs (BUT when the entire array has valid data, it returns numpy.ndarray)
            if isinstance(t_left, np.ma.core.MaskedArray):
                t_mask = t_left.mask
                t_left[t_mask] = np.nan
            if isinstance(s_left, np.ma.core.MaskedArray):
                s_mask = s_left.mask
                s_left[s_mask] = np.nan

            lons_left = self._lon[lon_w_idx:lon_e_idx + 1]
            for i in range(self._search_window):
                longitudes[i, 0:lons_left.size] = lons_left
            # logger.info("longitudes are now: %s" % longitudes)

            # --- Do the right portion of the array first, this will run into the wrap
            # longitude so limit it accordingly
            lon_w_idx = 0
            lon_e_idx = self._search_window - lons_left.size - 1

            # Need +1 on the north and east indices since it is the "stop" value in these slices
            t_right = self._file_temp.variables['temperature'][self._day_idx, :, lat_s_idx:lat_n_idx + 1,
                      lon_w_idx:lon_e_idx + 1]
            s_right = self._file_sal.variables['salinity'][self._day_idx, :, lat_s_idx:lat_n_idx + 1,
                      lon_w_idx:lon_e_idx + 1]
            # Set 'unfilled' elements to NANs (BUT when the entire array has valid data, it returns numpy.ndarray)
            if isinstance(t_right, np.ma.core.MaskedArray):
                t_mask = t_right.mask
                t_right[t_mask] = np.nan
            if isinstance(s_right, np.ma.core.MaskedArray):
                s_mask = s_right.mask
                s_right[s_mask] = np.nan

            lons_right = self._lon[lon_w_idx:lon_e_idx + 1]
            for i in range(self._search_window):
                longitudes[i, lons_left.size:self._search_window] = lons_right

            # merge data
            t = np.zeros((self._file_temp.variables['lev'].size, self._search_window, self._search_window))
            t[:, :, 0:lons_left.size] = t_left
            t[:, :, lons_left.size:self._search_window] = t_right
            s = np.zeros((self._file_temp.variables['lev'].size, self._search_window, self._search_window))
            s[:, :, 0:lons_left.size] = s_left
            s[:, :, lons_left.size:self._search_window] = s_right

        # Calculate distances from requested position to each of the grid node locations
        distances = np.zeros((self._d.size, self._search_window, self._search_window))
        latitudes = np.zeros((self._search_window, self._search_window))
        lats = self._lat[lat_s_idx:lat_n_idx + 1]
        for i in range(self._search_window):
            latitudes[:, i] = lats

        for i in range(self._search_window):

            for j in range(self._search_window):
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

        # Spin through all the depth levels
        temp_pot = np.zeros(self._d.size)
        temp_in_situ = np.zeros(self._d.size)
        d = np.zeros(self._d.size)
        sal = np.zeros(self._d.size)
        num_values = 0
        for i in range(self._d.size):

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
            # d_closest = d_level[ind2]

            temp_pot[i] = t_closest
            sal[i] = s_closest
            d[i] = self._d[i]

            # Calculate in-situ temperature
            p = Oc.d2p(d[i], lat)
            temp_in_situ[i] = Oc.in_situ_temp(s=sal[i], t=t_closest, p=p, pr=self._ref_p)
            # logger.info("%02d: %6.1f %6.1f > T/S/Dist: %3.1f %3.1f %3.1f [pot.temp. %3.1f]"
            #             % (i, d[i], p, temp_in_situ[i], s_closest, d_closest, t_closest))

            num_values += 1

        if num_values == 0:
            logger.info("no data from lookup!")
            return None

        # ind = np.nanargmin(distances[0])
        # ind2 = np.unravel_index(ind, distances[0].shape)
        # switching to the query location
        # lat_out = latitudes[ind2]
        # lon_out = longitudes[ind2]
        # while lon_out > 180.0:
        #     lon_out -= 360.0

        # Make a new SV object to return our query in
        ssp = Profile()
        ssp.meta.sensor_type = Dicts.sensor_types['Synthetic']
        ssp.meta.probe_type = Dicts.probe_types['RTOFS']
        ssp.meta.latitude = lat
        if lon > 180.0:  # Go back to negative longitude
            lon -= 360.0
        ssp.meta.longitude = lon
        ssp.meta.utc_time = dt(year=dtstamp.year, month=dtstamp.month, day=dtstamp.day,
                               hour=dtstamp.hour, minute=dtstamp.minute, second=dtstamp.second)
        ssp.meta.original_path = "RTOFS_%s" % dtstamp.strftime("%Y%m%d_%H%M%S")
        ssp.init_data(num_values)
        ssp.data.depth = d[0:num_values]
        ssp.data.temp = temp_in_situ[0:num_values]
        ssp.data.sal = sal[0:num_values]
        ssp.calc_data_speed()
        ssp.clone_data_to_proc()
        ssp.init_sis()

        profiles = ProfileList()
        profiles.append_profile(ssp)

        return profiles

    def clear_data(self) -> None:
        """Delete the data and reset the last loaded day"""
        logger.debug("clearing data")
        if self._has_data_loaded:
            if self._file_temp:
                self._file_temp.close()
            self._file_temp = None
            if self._file_sal:
                self._file_sal.close()
            self._file_sal = None
            self._lat = None
            self._lon = None
            self._lat_step = None
            self._lat_0 = None
            self._lon_step = None
            self._lon_0 = None
        self._has_data_loaded = False  # grids are "loaded" ? (netCDF files are opened)
        self._last_loaded_day = dt(1900, 1, 1)  # some silly day in the past
        self._day_idx = None

    def __repr__(self) -> str:
        msg = "%s" % super(Rtofs, self).__repr__()
        msg += "      <has data loaded: %s>\n" % (self._has_data_loaded,)
        msg += "      <last loaded day: %s>\n" % (self._last_loaded_day.strftime(r"%d\%m\%Y"),)
        return msg

    # ### private methods ###

    @staticmethod
    def _check_url(url: str) -> bool:
        try:
            with requests.get(url, allow_redirects=True, stream=True) as resp:
                logger.debug("passed url: %s -> %s" % (url, resp.status_code))
                if resp.status_code == 200:
                    return True
                else:
                    return False

        except Exception as e:
            logger.warning("while checking %s, %s" % (url, e))
            return False

    @staticmethod
    def _build_check_urls(input_date: date) -> tuple:
        """make up the url to use for salinity and temperature"""
        # Primary server: http://nomads.ncep.noaa.gov/pub/data/nccf/com/rtofs/prod/rtofs.20160410/
        url_temp = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/rtofs/prod/rtofs.%s/' \
                   'rtofs_glo_3dz_n024_daily_3ztio.nc' \
                   % input_date.strftime("%Y%m%d")
        logger.debug("check temp: %s" % url_temp)
        url_sal = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/rtofs/prod/rtofs.%s/' \
                  'rtofs_glo_3dz_n024_daily_3zsio.nc' \
                  % input_date.strftime("%Y%m%d")
        logger.debug("check sal: %s" % url_sal)
        return url_temp, url_sal

    @staticmethod
    def _build_opendap_urls(input_date: date) -> tuple:
        """make up the url to use for salinity and temperature"""
        # Primary server: http://nomads.ncep.noaa.gov/dods/rtofs
        url_temp = 'https://nomads.ncep.noaa.gov/dods/rtofs/rtofs_global%s/' \
                   'rtofs_glo_3dz_nowcast_daily_temp' \
                   % input_date.strftime("%Y%m%d")
        logger.debug("opendap temp: %s" % url_temp)
        url_sal = 'https://nomads.ncep.noaa.gov/dods/rtofs/rtofs_global%s/' \
                  'rtofs_glo_3dz_nowcast_daily_salt' \
                  % input_date.strftime("%Y%m%d")
        logger.debug("opendap sal: %s" % url_sal)
        return url_temp, url_sal

    def _download_files(self, datestamp: dt, server_mode: bool = False):
        """Actually, just try to connect with the remote files
        For a given queried date, we may have to use the forecast from the previous
        day since the current nowcast doesn't hold data for today (solved?)
        """
        progress = CliProgress()

        # check if the files are loaded and that the date matches
        if self._has_data_loaded:
            # logger.info("%s" % self.last_loaded_day)
            if self._last_loaded_day == datestamp:
                return True
            # the data are old
            logger.info("cleaning data: %s %s" % (self._last_loaded_day, datestamp))
            self.clear_data()

        progress.start(text="Download RTOFS", is_disabled=server_mode)

        # check if the data are available on the RTOFS server
        url_ck_temp, url_ck_sal = self._build_check_urls(datestamp)
        if not self._check_url(url_ck_temp) or not self._check_url(url_ck_sal):

            logger.info('issue with %s -> trying with the previous day' % datestamp)
            datestamp -= timedelta(days=1)
            url_ck_temp, url_ck_sal = self._build_check_urls(datestamp)

            if not self._check_url(url_ck_temp) or not self._check_url(url_ck_sal):
                logger.warning('unable to retrieve data from RTOFS server for date: %s and next day' % datestamp)
                self.clear_data()
                progress.end()
                return False

        progress.update(30)

        # Try to download the data grid grids
        url_temp, url_sal = self._build_opendap_urls(datestamp)
        # logger.debug('downloading RTOFS data for %s' % datestamp)
        try:
            self._file_temp = Dataset(url_temp)
            progress.update(60)
            self._file_sal = Dataset(url_sal)
            progress.update(80)
            self._day_idx = 1  # it was 3 1-day steps, now only 2 steps

        except (RuntimeError, IOError) as e:
            logger.warning("unable to access data: %s -> %s" % (datestamp.strftime("%Y%m%d"), e))
            self.clear_data()
            progress.end()
            return False

        # success!
        self._has_data_loaded = True
        self._last_loaded_day = datestamp
        # logger.info("loaded data for %s" % datestamp)
        progress.end()
        return True

    def grid_coords(self, lat: float, lon: float, dtstamp: dt, server_mode: Optional[bool] = False) -> tuple:
        """Convert the passed position in RTOFS grid coords"""

        # check if we need to update the data set (new day!)
        if not self.download_db(dtstamp, server_mode=server_mode):
            logger.error("troubles in updating data set for timestamp: %s" % dtstamp.strftime("%Y%m%d"))
            return None, None

        # make longitude "safe" since RTOFS grid starts at east longitude 70-ish degrees
        if lon < self._lon_0:
            lon += 360.0

        # This does a nearest neighbour lookup
        lat_idx = int(round((lat - self._lat_0) / self._lat_step, 0))
        lon_idx = int(round((lon - self._lon_0) / self._lon_step, 0))

        return lat_idx, lon_idx
