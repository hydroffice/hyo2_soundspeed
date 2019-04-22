from datetime import datetime as dt, date, timedelta
from enum import IntEnum
from http import client
import logging
import socket
from typing import Optional, Union
from urllib import parse

from netCDF4 import Dataset
import numpy as np

from hyo2.abc.lib.progress.cli_progress import CliProgress

from hyo2.soundspeed.atlas.abstract import AbstractAtlas
from hyo2.soundspeed.profile.profile import Profile
from hyo2.soundspeed.profile.profilelist import ProfileList
from hyo2.soundspeed.profile.dicts import Dicts
from hyo2.soundspeed.profile.oceanography import Oceanography as Oc

logger = logging.getLogger(__name__)


class RegOfs(AbstractAtlas):
    """GoMOFS atlas"""

    class Model(IntEnum):

        CBOFS = 10      # RG = True     # Format is GoMOFS
        DBOFS = 11      # RG = True     # Format is GoMOFS
        GoMOFS = 12     # RG = True     # Format is GoMOFS
        NYOFS = 13      # RG = False
        SJROFS = 14     # RG = False

        NGOFS = 20      # RG = True     # Format is GoMOFS
        TBOFS = 21      # RG = True     # Format is GoMOFS

        LEOFS = 30      # RG = True     # Format is GoMOFS
        LHOFS = 31      # RG = False
        LMOFS = 32      # RG = False
        LOOFS = 33      # RG = False
        LSOFS = 34      # RG = False

        CREOFS = 40     # RG = True     # Format is GoMOFS
        SFBOFS = 41     # RG = True     # Format is GoMOFS

    regofs_model_descs = {
        Model.CBOFS: "Chesapeake Bay Operational Forecast System",
        Model.DBOFS: "Delaware Bay Operational Forecast System",
        Model.GoMOFS: "Gulf of Maine Operational Forecast System",
        Model.NYOFS: "Port of New York and New Jersey Operational Forecast System",
        Model.SJROFS: "St. John's River Operational Forecast System",
        Model.NGOFS: "Northern Gulf of Mexico Operational Forecast System",
        Model.TBOFS: "Tampa Bay Operational Forecast System",
        Model.LEOFS: "Lake Erie Operational Forecast System",
        Model.LHOFS: "Lake Huron Operational Forecast System",
        Model.LMOFS: "Lake Michigan Operational Forecast System",
        Model.LOOFS: "Lake Ontario Operational Forecast System",
        Model.LSOFS: "Lake Superior Operational Forecast System",
        Model.CREOFS: "Columbia River Estuary Operational Forecast System",
        Model.SFBOFS: "San Francisco Bay Operational Forecast System"
    }

    def __init__(self, data_folder: str, prj: 'hyo2.soundspeed.soundspeed import SoundSpeedLibrary',
                 model: Model) -> None:
        super().__init__(data_folder=data_folder, prj=prj)
        self.model = model
        self.name = model.name
        self.desc = self.regofs_model_descs[model]

        # How far are we willing to look for solutions? size in grid nodes
        self._search_window = 5
        self._search_half_window = self._search_window // 2
        # 2000 dBar is the ref depth associated with the potential temperatures in the grid (sigma-2)
        self._ref_p = 2000

        self._has_data_loaded = False  # grids are "loaded" ? (netCDF files are opened)
        self._last_loaded_day = date(1900, 1, 1)  # some silly day in the past
        self._file = None
        self._day_idx = None
        self._d = None
        self._lat = None
        self._lon = None
        self._lat_step = None
        self._lat_min = None
        self._lat_max = None
        self._lon_step = None
        self._lon_min = None
        self._lon_max = None

    # ### public API ###

    def is_present(self) -> bool:
        """check the availability"""
        return self._has_data_loaded

    def download_db(self, datestamp: Union[date, dt, None] = None, server_mode: bool = False) -> bool:
        """try to connect and load info from the data set"""
        if datestamp is None:
            datestamp = dt.utcnow()
        if isinstance(datestamp, dt):
            datestamp = datestamp.date()
        if not isinstance(datestamp, date):
            raise RuntimeError("invalid date passed: %s" % type(datestamp))

        if not self._download_files(datestamp=datestamp, server_mode=server_mode):
            return False

        try:
            # Now get latitudes, longitudes and depths for x,y,z referencing
            self._d = self._file.variables['Depth'][:]
            self._lat = self._file.variables['Latitude'][:]
            self._lon = self._file.variables['Longitude'][:]
            # logger.debug('d:(%s)\n%s' % (self._d.shape, self._d))
            # logger.debug('lat:(%s)\n%s' % (self._lat.shape, self._lat))
            # logger.debug('lon:(%s)\n%s' % (self._lon.shape, self._lon))

        except Exception as e:
            logger.error("troubles in variable lookup for lat/long grid and/or depth: %s" % e)
            self.clear_data()
            return False

        self._lat_min = self._lat[0, 0]
        self._lat_max = self._lat[-1, 0]
        self._lat_step = self._lat[1, 0] - self._lat_min
        self._lon_min = self._lon[0, 0]
        self._lon_max = self._lon[0, -1]
        self._lon_step = self._lon[0, 1] - self._lon_min

        logger.debug("0(%.3f, %.3f); -1(%.3f, %.3f); step(%.3f, %.3f)"
                     % (self._lat_min, self._lon_min, self._lat_max, self._lon_max, self._lat_step, self._lon_step))
        return True

    def query(self, lat: Optional[float], lon: Optional[float], datestamp: Union[date, dt, None] = None,
              server_mode: bool = False):
        """Query OFS for passed location and timestamp"""
        if datestamp is None:
            datestamp = dt.utcnow()
        if isinstance(datestamp, dt):
            datestamp = datestamp.date()
        if not isinstance(datestamp, date):
            raise RuntimeError("invalid date passed: %s" % type(datestamp))
        logger.debug("query: %s @ (%.6f, %.6f)" % (datestamp, lon, lat))

        # check the inputs
        if (lat is None) or (lon is None) or (datestamp is None):
            logger.error("invalid query: %s @ (%s, %s)" % (datestamp.strftime("%Y%m%d"), lon, lat))
            return None

        try:
            lat_idx, lon_idx = self.grid_coords(lat, lon, datestamp=datestamp, server_mode=server_mode)
            if lat_idx is None:
                logger.info("location outside of %s coverage" % self.name)
                return None

        except TypeError as e:
            logger.critical("while converting location to grid coords, %s" % e)
            return None

        logger.debug("idx > lat: %s, lon: %s" % (lat_idx, lon_idx))
        lat_s_idx = lat_idx - self._search_half_window
        if lat_s_idx < 0:
            lat_s_idx = 0
        lat_n_idx = lat_idx + self._search_half_window
        if lat_n_idx >= self._lat.shape[0]:
            lat_n_idx = self._lat.shape[0] - 1
        lon_w_idx = lon_idx - self._search_half_window
        if lon_w_idx < 0:
            lon_w_idx = 0
        lon_e_idx = lon_idx + self._search_half_window
        if lon_e_idx >= self._lon.shape[1]:
            lon_e_idx = self._lon.shape[1] - 1
        # logger.info("indices -> %s %s %s %s" % (lat_s_idx, lat_n_idx, lon_w_idx, lon_e_idx))
        lat_search_window = lat_n_idx - lat_s_idx + 1
        lon_search_window = lon_e_idx - lon_w_idx + 1
        logger.info("updated search window: (%s, %s)" % (lat_search_window, lon_search_window))

        # Need +1 on the north and east indices since it is the "stop" value in these slices
        t = self._file.variables['temp'][self._day_idx, :, lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]
        s = self._file.variables['salt'][self._day_idx, :, lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]
        # Set 'unfilled' elements to NANs (BUT when the entire array has valid data, it returns numpy.ndarray)
        if isinstance(t, np.ma.core.MaskedArray):
            t_mask = t.mask
            t._sharedmask = False
            t[t_mask] = np.nan
        if isinstance(s, np.ma.core.MaskedArray):
            s_mask = s.mask
            s._sharedmask = False
            s[s_mask] = np.nan

        # Calculate distances from requested position to each of the grid node locations
        distances = np.zeros((self._d.size, lon_search_window, lat_search_window))
        longitudes = self._lon[lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]
        latitudes = self._lat[lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]

        for i in range(lat_search_window):

            for j in range(lon_search_window):
                dist = self.g.distance(longitudes[i, j], latitudes[i, j], lon, lat)
                distances[:, i, j] = dist
                # logger.info("node (%s %s), pos: %3.2f, %3.2f, dist: %3.1f"
                #             % (i, j, latitudes[i, j], longitudes[i, j], distances[0, i, j]))

        # Get mask of "no data" elements and replace these with NaNs in distance array
        t_mask = np.isnan(t)
        distances[t_mask] = np.nan
        s_mask = np.isnan(s)
        distances[s_mask] = np.nan
        # logger.info("distance array:\n%s" % distances[0])

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
        ssp.meta.probe_type = Dicts.probe_types[self.name]
        ssp.meta.latitude = lat
        if lon > 180.0:  # Go back to negative longitude
            lon -= 360.0
        ssp.meta.longitude = lon
        ssp.meta.utc_time = dt(year=datestamp.year, month=datestamp.month, day=datestamp.day)
        ssp.meta.original_path = "%s_%s" % (self.name, datestamp.strftime("%Y%m%d"))
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
            if self._file:
                self._file.close()
            self._file = None
            self._lat = None
            self._lon = None
            self._lat_step = None
            self._lat_min = None
            self._lat_max = None
            self._lon_step = None
            self._lon_min = None
            self._lon_max = None
        self._has_data_loaded = False  # grids are "loaded" ? (netCDF files are opened)
        self._last_loaded_day = date(1900, 1, 1)  # some silly day in the past
        self._day_idx = None

    def __repr__(self):
        msg = "%s" % super().__repr__()
        msg += "      <has data loaded: %s>\n" % (self._has_data_loaded,)
        msg += "      <last loaded day: %s>\n" % (self._last_loaded_day.strftime(r"%d\%m\%Y"),)
        return msg

    # ### private methods ###

    @staticmethod
    def _check_url(url: str) -> bool:
        try:
            p = parse.urlparse(url)
            conn = client.HTTPSConnection(p.netloc)
            conn.request('HEAD', p.path)
            resp = conn.getresponse()
            conn.close()
            logger.debug("passed url: %s -> %s" % (url, resp.status))

        except socket.error as e:
            logger.warning("while checking %s, %s" % (url, e))
            return False

        return resp.status < 400

    @staticmethod
    def _build_check_url(input_date: date, name: str) -> str:
        """make up the url to use for salinity and temperature"""
        # Primary server: https://opendap.co-ops.nos.noaa.gov/thredds/fileServer/NOAA/GOMOFS/MODELS/201901/
        #                 nos.gomofs.regulargrid.n006.20190115.t18z.nc
        url = 'https://opendap.co-ops.nos.noaa.gov/thredds/fileServer/NOAA/%s/MODELS/%s/' \
              'nos.%s.regulargrid.n003.%s.t00z.nc' \
              % (name.upper(), input_date.strftime("%Y%m"), name.lower(), input_date.strftime("%Y%m%d"))
        return url

    @staticmethod
    def _build_opendap_url(input_date: date, name: str) -> str:
        """make up the url to use for salinity and temperature"""
        # Primary server: https://opendap.co-ops.nos.noaa.gov/thredds/dodsC/NOAA/GOMOFS/MODELS/201901/
        #                 nos.gomofs.regulargrid.n006.20190115.t18z.nc
        url = 'https://opendap.co-ops.nos.noaa.gov/thredds/dodsC/NOAA/%s/MODELS/%s/' \
              'nos.%s.regulargrid.n003.%s.t00z.nc' \
              % (name.upper(), input_date.strftime("%Y%m"), name.lower(), input_date.strftime("%Y%m%d"))
        return url

    def _download_files(self, datestamp: date, server_mode: bool = False):
        """Actually, just try to connect with the remote files
        For a given queried date, we may have to use the forecast from the previous
        day since the current nowcast doesn't hold data for today (solved?)
        """
        progress = CliProgress()

        if not isinstance(datestamp, date):
            raise RuntimeError("invalid date passed: %s" % type(datestamp))

        # check if the files are loaded and that the date matches
        if self._has_data_loaded:
            # logger.info("%s" % self.last_loaded_day)
            if self._last_loaded_day == datestamp:
                return True
            else:  # the data are old
                logger.info("cleaning data: %s %s" % (self._last_loaded_day, datestamp))
                self.clear_data()

        progress.start(text="Download %s" % self.name, is_disabled=server_mode)

        # check if the data are available on the RTOFS server
        url_ck = self._build_check_url(datestamp, self.name)
        if not self._check_url(url_ck):

            datestamp -= timedelta(days=1)
            url_ck = self._build_check_url(datestamp, self.name)

            if not self._check_url(url_ck):
                logger.warning('unable to retrieve data from %s server for date: %s and next day'
                               % (self.name, datestamp))
                self.clear_data()
                progress.end()
                return False

        progress.update(30)

        # Try to download the data grid grids
        url = self._build_opendap_url(datestamp, self.name)
        # logger.debug('downloading RTOFS data for %s' % datestamp)
        try:
            self._file = Dataset(url)
            progress.update(70)
            self._day_idx = 0

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

    def grid_coords(self, lat: float, lon: float, datestamp: date, server_mode: Optional[bool] = False) -> tuple:
        """Convert the passed position in OFS grid coords"""

        # check if we need to update the data set (new day!)
        if not self.download_db(datestamp, server_mode=server_mode):
            logger.error("troubles in updating data set for timestamp: %s" % datestamp.strftime("%Y%m%d"))
            raise RuntimeError('troubles in db download')

        # check validity of longitude and latitude
        if lon < (self._lon_min - self._lon_step / 2.0):
            return None, None
        if lat < (self._lat_min - self._lat_step / 2.0):
            return None, None
        if lon > (self._lon_max + self._lon_step / 2.0):
            return None, None
        if lat > (self._lat_max + self._lat_step / 2.0):
            return None, None

        # This does a nearest neighbour lookup
        lat_idx = int(round((lat - self._lat_min) / self._lat_step, 0))
        lon_idx = int(round((lon - self._lon_min) / self._lon_step, 0))

        return lat_idx, lon_idx
