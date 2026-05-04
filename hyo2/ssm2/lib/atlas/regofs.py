from datetime import datetime, timezone, timedelta
import logging
from typing import TYPE_CHECKING

from numpy import full_like, isnan, nan, ma, zeros, nanargmin, unravel_index
from numpy import typing
from netCDF4 import Dataset, num2date

# noinspection PyUnresolvedReferences
from hyo2.abc2.lib.package.pkg_helper import PkgHelper
# noinspection PyUnresolvedReferences
from hyo2.abc2.lib.progress.cli_progress import CliProgress
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.atlas.regofs_model import RegOfsModel
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.atlas.abstract import AbstractAtlas
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.profile.dicts import Dicts
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.profile.oceanography import Oceanography as Oc
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.profile.profile import Profile
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.profile.profilelist import ProfileList


if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary


logger = logging.getLogger(__name__)


class RegOfs(AbstractAtlas):

    def __init__(self, data_folder: str, prj: 'SoundSpeedLibrary',
                 model: RegOfsModel) -> None:
        super().__init__(data_folder=data_folder, prj=prj)
        self.model: RegOfsModel = model
        self.name: str = model.name
        self.desc: str = model.description
        
        # How far are we willing to look for solutions? size in grid nodes
        self._search_window: int = 5
        self._search_half_window: int = self._search_window // 2
        # 2000 dBar is the ref depth associated with the potential temperatures in the grid (sigma-2)
        self._ref_p: float = 2000.0
        
        self._has_data_loaded: bool = False  # grids are "loaded" ? (netCDF files are opened)
        self._last_loaded_day: datetime = datetime(1900, 1, 1)  # some silly day in the past
        self._file = None
        self._day_idx: int | None = None
        self._d = None
        self._lat: typing.NDArray | None = None
        self._lon: typing.NDArray | None = None
        self._lat_step: float | None = None
        self._lat_min: float | None = None
        self._lat_max: float | None = None
        self._lon_step: float | None = None
        self._lon_min: float | None = None
        self._lon_max: float | None = None
        
    @property
    def lat_step(self) -> float:
        if self._lat_step is None:
            raise RuntimeError("_lat_step is unset")
        return self._lat_step
        
    @property
    def lat_min(self) -> float:
        if self._lat_min is None:
            raise RuntimeError("_lat_min in unset")
        return self._lat_min
    
    @property
    def lat_max(self) -> float:
        if self._lat_max is None:
            raise RuntimeError("_lat_max in unset")
        return self._lat_max

    @property
    def lon_step(self) -> float:
        if self._lon_step is None:
            raise RuntimeError("_lon_step is unset")
        return self._lon_step

    @property
    def lon_min(self) -> float:
        if self._lon_min is None:
            raise RuntimeError("_lon_min in unset")
        return self._lon_min

    @property
    def lon_max(self) -> float:
        if self._lon_max is None:
            raise RuntimeError("_lon_max in unset")
        return self._lon_max
    
    # is_present function
        
    def is_present(self) -> bool:
        """check the availability"""
        return self._has_data_loaded
    
    # query function
    
    def query(self, lat: float, lon: float, datestamp: datetime | None = None, server_mode: bool = False):
        """Query OFS for passed location and timestamp"""
        if datestamp is None:
            datestamp: datetime = datetime.now(tz=timezone.utc)

        logger.debug("query: %s @ (%.6f, %.6f)" % (datestamp, lon, lat))

        try:
            lat_idx, lon_idx = self.grid_coords(lat, lon, datestamp=datestamp, server_mode=server_mode)
            if lat_idx is None:
                logger.info("troubles with data source or location outside of %s coverage" % self.name)
                return None

        except TypeError as e:
            logger.critical("while converting location to grid coords, %s" % e)
            return None

        ocean_time = self._file.variables['time']
        datetime_retrieved = num2date(ocean_time[0], units=ocean_time.units, calendar=ocean_time.calendar)
        logger.debug(("Query datetime: %s" % datestamp.isoformat()))
        logger.debug("Retrieved datetime: %s" % datetime_retrieved.isoformat())

        if self._lon is None:
            raise RuntimeError("_lon is unset")
        if self._lat is None:
            raise RuntimeError("_lat is unset")

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
        t = self._file.variables['temp'][self._day_idx, :][..., lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]
        # logger.debug('t shape: %s' % (t.shape, ))
        # https://ponce.sdsu.edu/lakesalinityworld.html#:~:text=The%20salinity%20of%20Lake%20Superior,between%200.05%20and%200.60%20ppt.
        if self.model == RegOfsModel.LMHOFS:
            s = full_like(t, 0.3)
        elif self.model == RegOfsModel.LOOFS:
            s = full_like(t, 0.5)
        else:
            s = self._file.variables['salt'][self._day_idx, :][..., lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]
        # Set 'unfilled' elements to NANs (BUT when the entire array has valid data, it returns numpy.ndarray)
        if isinstance(t, ma.core.MaskedArray):
            t_mask = t.mask
            t._sharedmask = False
            t[t_mask] = nan
        if isinstance(s, ma.core.MaskedArray):
            s_mask = s.mask
            s._sharedmask = False
            s[s_mask] = nan

        # Calculate distances from requested position to each of the grid node locations
        distances = zeros((self._d.size, lon_search_window, lat_search_window))
        # logger.debug('distances shape: %s' % (distances.shape,))
        longitudes = self._lon[lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]
        latitudes = self._lat[lat_s_idx:lat_n_idx + 1, lon_w_idx:lon_e_idx + 1]

        for i in range(lat_search_window):

            for j in range(lon_search_window):
                dist = self.g.distance(longitudes[i, j], latitudes[i, j], lon, lat)
                distances[:, i, j] = dist
                # logger.info("node (%s %s), pos: %3.2f, %3.2f, dist: %3.1f"
                #             % (i, j, latitudes[i, j], longitudes[i, j], distances[0, i, j]))

        # Get mask of "no data" elements and replace these with NaNs in distance array
        t_mask = isnan(t)
        distances[t_mask] = nan
        s_mask = isnan(s)
        distances[s_mask] = nan
        # logger.info("distance array:\n%s" % distances[0])

        # Spin through all the depth levels
        temp_pot = zeros(self._d.size)
        temp_in_situ = zeros(self._d.size)
        d = zeros(self._d.size)
        sal = zeros(self._d.size)
        num_values = 0
        for i in range(self._d.size):

            t_level = t[i]
            s_level = s[i]
            d_level = distances[i]

            try:
                ind = nanargmin(d_level)
            except ValueError:
                # logger.info("%s: all-NaN slices" % i)
                continue

            if isnan(ind):
                logger.info("%s: bottom of valid data" % i)
                break

            ind2 = unravel_index(ind, t_level.shape)

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

        # Make a new SV object to return our query in
        ssp = Profile()
        ssp.meta.sensor_type = Dicts.sensor_types['Synthetic']
        ssp.meta.probe_type = Dicts.probe_types[self.name]
        ssp.meta.latitude = lat
        if lon > 180.0:  # Go back to negative longitude
            lon -= 360.0
        ssp.meta.longitude = lon
        ssp.meta.utc_time = datetime(year=datestamp.year, month=datestamp.month, day=datestamp.day,
                               hour=datestamp.hour, minute=datestamp.minute, second=datestamp.second)
        ssp.meta.original_path = "%s_%s" % (self.name, datestamp.strftime("%Y%m%d_%H%M%S"))
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
    
    def grid_coords(self, lat: float, lon: float, datestamp: datetime, server_mode: bool = False) -> tuple:
        """Convert the passed position in OFS grid coords"""

        # check if we need to update the data set (new day!)
        if not self.download_db(datestamp, server_mode=server_mode):
            logger.error("troubles in updating data set for timestamp: %s" % datestamp.strftime("%Y/%m/%d %H:%M:%S"))
            return None, None

        # check validity of longitude and latitude
        if lon < (self.lon_min - self.lon_step / 2.0):
            return None, None
        if lat < (self.lat_min - self.lat_step / 2.0):
            return None, None
        if lon > (self.lon_max + self.lon_step / 2.0):
            return None, None
        if lat > (self.lat_max + self.lat_step / 2.0):
            return None, None

        # This does a nearest neighbor lookup
        lat_idx = int(round((lat - self._lat_min) / self._lat_step, 0))
        lon_idx = int(round((lon - self._lon_min) / self._lon_step, 0))

        return lat_idx, lon_idx

    # download_db function

    def download_db(self, datestamp: datetime | None = None, server_mode: bool = False) -> bool:
        """try to connect and load info from the data set"""
        if datestamp is None:
            datestamp: datetime = datetime.now(tz=timezone.utc)

        if not self._download_files(datestamp=datestamp, server_mode=server_mode):
            return False

        try:
            # Now get latitudes, longitudes and depths for x,y,z referencing
            self._d = self._file.variables['Depth'][:]
            self._lat: typing.NDArray = self._file.variables['Latitude'][:]
            self._lon: typing.NDArray = self._file.variables['Longitude'][:]
            # logger.debug('d:(%s)\n%s' % (self._d.shape, self._d))
            # logger.debug('lat:(%s)\n%s' % (self._lat.shape, self._lat))
            # logger.debug('lon:(%s)\n%s' % (self._lon.shape, self._lon))

        except Exception as e:
            logger.error("troubles in variable lookup for lat/long grid and/or depth: %s" % e)
            self.clear_data()
            return False

        if self._lon is None:
            raise RuntimeError("_lon is unset")
        if self._lat is None:
            raise RuntimeError("_lat is unset")

        self._lat_min = self._lat[0, 0]
        self._lat_max = self._lat[-1, 0]
        self._lat_step = self._lat[1, 0] - self.lat_min
        self._lon_min = self._lon[0, 0]
        self._lon_max = self._lon[0, -1]
        self._lon_step = self._lon[0, 1] - self.lon_min

        logger.debug("0(%.3f, %.3f); -1(%.3f, %.3f); step(%.3f, %.3f)"
                     % (self.lat_min, self.lon_min, self.lat_max, self.lon_max, self.lat_step, self.lon_step))
        return True
    
    def _download_files(self, datestamp: datetime, server_mode: bool = False) -> bool:
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
            else:  # the data are old
                logger.info("cleaning data: %s %s" % (self._last_loaded_day, datestamp))
                self.clear_data()

        progress.start(text="Connect to %s" % self.name, is_disabled=server_mode)

        # check if the data are available on the RTOFS server
        url = self.model.valid_opendap_url(input_date=datestamp)
        if not url:
            logger.warning('unable to retrieve data from %s server for date: %s and previous day'
                           % (self.name, datestamp))
            self.clear_data()
            progress.end()
            return False

        progress.update(30)

        # Try to open the data grid grids
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
        progress.end()
        return True

    # Other methods

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
        self._last_loaded_day = datetime(1900, 1, 1)  # some silly day in the past
        self._day_idx = None

    def __repr__(self):
        msg = "%s" % super().__repr__()
        msg += "      <has data loaded: %s>\n" % (self._has_data_loaded,)
        msg += "      <last loaded day: %s>\n" % (self._last_loaded_day.strftime(r"%d\%m\%Y"),)
        return msg
