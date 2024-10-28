import math
import os.path
from datetime import datetime as dt, date, timedelta
import logging
import shutil
from typing import TYPE_CHECKING

from netCDF4 import Dataset
import numpy as np
import requests

from hyo2.abc2.lib.progress.cli_progress import CliProgress

from hyo2.ssm2.lib.atlas.abstract import AbstractAtlas
from hyo2.ssm2.lib.profile.profile import Profile
from hyo2.ssm2.lib.profile.profilelist import ProfileList
from hyo2.ssm2.lib.profile.dicts import Dicts
from hyo2.ssm2.lib.profile.oceanography import Oceanography as Oc

if TYPE_CHECKING:
    from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger(__name__)


class Rtofs(AbstractAtlas):
    """RTOFS atlas"""

    def __init__(self, data_folder: str, prj: 'SoundSpeedLibrary') -> None:
        super(Rtofs, self).__init__(data_folder=data_folder, prj=prj)
        self.name = self.__class__.__name__
        self.desc = "Global Real-Time Ocean Forecast System"

        # 2000 dBar is the ref depth associated with the potential temperatures in the grid (sigma-2)
        self._ref_p = 2000

        self._has_data_loaded = False
        self._last_loaded_day = dt(1900, 1, 1)  # some silly day in the past
        self._file_temp = None
        self._file_sal = None
        self._day_idx = None
        self._d = None
        self._lat = None
        self._lon = None

    def clear_data(self) -> None:
        """Delete the data and reset the last loaded day"""
        logger.debug("clearing data")
        self._has_data_loaded = False
        self._last_loaded_day = dt(1900, 1, 1)  # some silly day in the past
        if self._file_temp:
            self._file_temp.close()
        self._file_temp = None
        if self._file_sal:
            self._file_sal.close()
        self._file_sal = None
        self._day_idx = None
        self._d = None
        self._lat = None
        self._lon = None

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
                   'rtofs_glo_3dz_n024_daily_3ztio.nc' % input_date.strftime("%Y%m%d")
        logger.debug("target RTOFS temp: %s" % url_temp)
        url_sal = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/rtofs/prod/rtofs.%s/' \
                  'rtofs_glo_3dz_n024_daily_3zsio.nc' % input_date.strftime("%Y%m%d")
        logger.debug("target RTOFS sal: %s" % url_sal)
        return url_temp, url_sal

    @staticmethod
    def _build_opendap_urls(input_date: date) -> tuple:
        """make up the url to use for salinity and temperature"""
        # TODO: currently unused!

        # Primary server: http://nomads.ncep.noaa.gov/dods/rtofs
        url_temp = 'https://nomads.ncep.noaa.gov/dods/rtofs/rtofs_global%s/rtofs_glo_3dz_nowcast_daily_temp' \
                   % input_date.strftime("%Y%m%d")
        logger.debug("OpenDAP temp: %s" % url_temp)
        url_sal = 'https://nomads.ncep.noaa.gov/dods/rtofs/rtofs_global%s/rtofs_glo_3dz_nowcast_daily_salt' \
                  % input_date.strftime("%Y%m%d")
        logger.debug("OpenDAP sal: %s" % url_sal)
        return url_temp, url_sal

    def is_present(self) -> bool:
        """check the availability"""
        return self._has_data_loaded

    def _clean_rtofs_folder(self, skip_folder: str | None = None) -> None:
        # logger.debug("RTOFS folder to clean: %s" % self.data_folder)
        for item in os.listdir(self.data_folder):
            full_path = os.path.join(self.data_folder, item)

            if os.path.isfile(full_path):
                os.remove(full_path)
                continue

            if skip_folder:
                if item == skip_folder:
                    continue
            shutil.rmtree(full_path)

    def _download_files(self, datestamp: dt, server_mode: bool = False) -> bool:
        progress = CliProgress()

        # check if the files are loaded and that the date matches
        if self._has_data_loaded:
            # logger.info("%s" % self.last_loaded_day)
            if self._last_loaded_day == datestamp:
                return True
            # the data are old
            logger.info("cleaning data: %s %s" % (self._last_loaded_day, datestamp))
            self.clear_data()

        progress.start(text="Check RTOFS urls", is_disabled=server_mode)

        # check if the data are available on the RTOFS server
        url_ck_temp, url_ck_sal = self._build_check_urls(datestamp)
        if not self._check_url(url_ck_temp) or not self._check_url(url_ck_sal):

            logger.info('issue with %s -> trying with the previous day' % datestamp)
            datestamp -= timedelta(days=1)
            url_ck_temp, url_ck_sal = self._build_check_urls(datestamp)

            if not self._check_url(url_ck_temp) or not self._check_url(url_ck_sal):
                logger.warning('unable to locate data on RTOFS server for date: %s and next day' % datestamp)
                self.clear_data()
                progress.end()
                return False

        try:
            progress.update(text="Delete old RTOFS files", value=30)

            # remove all the RTOFS folder content, except the current date folder
            datestamp_name = datestamp.strftime("%Y%m%d")
            self._clean_rtofs_folder(skip_folder=datestamp_name)

            progress.update(text="Download RTOFS temperature", value=40)

            datestamp_folder = os.path.join(self.data_folder, datestamp_name)
            if not os.path.exists(datestamp_folder):
                os.makedirs(datestamp_folder)

            loc_file_temp = os.path.basename(url_ck_temp)
            loc_path_temp = os.path.join(datestamp_folder, loc_file_temp)
            logger.info('local temp: %s' % loc_path_temp)
            if not os.path.exists(loc_path_temp):
                progress.update(value=50)
                with requests.get(url_ck_temp, stream=True) as r:
                    with open(loc_path_temp, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
            self._file_temp = Dataset(loc_path_temp)

            progress.update(text="Download RTOFS salinity", value=60)

            loc_file_sal = os.path.basename(url_ck_sal)
            loc_path_sal = os.path.join(datestamp_folder, loc_file_sal)
            logger.info('local sal: %s' % loc_path_sal)
            if not os.path.exists(loc_path_sal):
                progress.update(value=75)
                with requests.get(url_ck_sal, stream=True) as r:
                    with open(loc_path_sal, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
            self._file_sal = Dataset(loc_path_sal)

            self._day_idx = 0

        except (RuntimeError, IOError) as e:
            logger.warning("unable to download RTOFS data: %s -> %s" % (datestamp.strftime("%Y%m%d"), e), exc_info=True)
            self.clear_data()
            self._clean_rtofs_folder()
            progress.end()
            return False

        # success!
        self._has_data_loaded = True
        self._last_loaded_day = datestamp
        # logger.info("loaded data for %s" % datestamp)
        progress.end()
        return True

    def download_db(self, dtstamp: dt | None = None, server_mode: bool = False) -> bool:
        """try to connect and load info from the data set"""
        if dtstamp is None:
            dtstamp = dt.utcnow()

        if not self._download_files(datestamp=dtstamp, server_mode=server_mode):
            return False

        try:
            self._d = self._file_temp.variables['Depth'][:]
            self._lat = self._file_temp.variables['Latitude'][:]
            self._lon = self._file_temp.variables['Longitude'][:]

            # logger.debug('d:(%s)\n%s' % (self._d.shape, self._d))
            # logger.debug('lat:(%s)\n%s' % (self._lat.shape, self._lat))
            # logger.debug('lon:(%s)\n%s' % (self._lon.shape, self._lon))

        except Exception as e:
            logger.error("troubles in variable lookup for lat/long grid and/or depth: %s" % e)
            self.clear_data()
            self._clean_rtofs_folder()
            return False

        return True

    def grid_coords(self, lat: float, lon: float, dtstamp: dt, server_mode: bool | None = False) -> tuple:
        """Convert the passed position in RTOFS grid coords"""

        # check if we need to update the data set (new day!)
        if not self.download_db(dtstamp, server_mode=server_mode):
            logger.error("troubles in downloading RTOFS data for timestamp: %s" % dtstamp.strftime("%Y%m%d"))
            return None, None

        # make longitude "safe" since RTOFS grid starts at east longitude 70-ish degrees
        if lon < self._lon.min():
            lon += 360.0

        # logger.debug("min/max lon: %s %s" % (self._lon.min(), self._lon.max()))
        # logger.debug("min/max lat: %s %s" % (self._lat.min(), self._lat.max()))

        delta_lat = self._lat - lat
        delta_lon = self._lon - lon
        # logger.debug("delta lat:(%s)\n%s" % (delta_lat.shape, delta_lat))
        # logger.debug("delta lon:(%s)\n%s" % (delta_lon.shape, delta_lon))
        dist_square = delta_lon * delta_lon + delta_lat * delta_lat
        # logger.debug("dist_square:(%s)\n%s" % (dist_square.shape, dist_square))
        lat_idx, lon_idx = np.unravel_index(np.nanargmin(dist_square), dist_square.shape)
        d2 = dist_square[lat_idx, lon_idx]
        if d2 > 0.04:
            logger.info("Located RTOFS point is too far: %s deg" % math.sqrt(d2))
            return None, None
        logger.debug("Valid RTOFS idx: (%s, %s) d: %s > lat: %s, lon: %s"
                     % (lat_idx, lon_idx, d2, self._lat[lat_idx, lon_idx], self._lon[lat_idx, lon_idx]))

        return lat_idx, lon_idx

    def query(self, lat: float | None, lon: float | None, dtstamp: dt | None = None, server_mode: bool = False):
        """Query RTOFS for passed location and timestamp"""
        if dtstamp is None:
            dtstamp = dt.utcnow()

        # check the inputs
        if (lat is None) or (lon is None):
            logger.error("invalid query: %s @ (%s, %s)" % (dtstamp.strftime("%Y/%m/%d %H:%M:%S"), lon, lat))
            return None
        logger.debug("query: %s @ (%.6f, %.6f)" % (dtstamp.strftime("%Y/%m/%d %H:%M:%S"), lon, lat))

        try:
            lat_idx, lon_idx = self.grid_coords(lat, lon, dtstamp=dtstamp, server_mode=server_mode)
            if lat_idx is None:
                logger.info("troubles with data source or location outside of %s coverage" % self.name)
                return None

        except TypeError as e:
            logger.critical("while converting location to grid coords, %s" % e, exc_info=True)
            return None

        # logger.debug("RTOFS idx: (%s, %s)" % (lat_idx, lon_idx))

        # Spin through all the depth levels
        temp_pot = np.zeros(self._d.size)
        temp_in_situ = np.zeros(self._d.size)
        d = np.zeros(self._d.size)
        sal = np.zeros(self._d.size)
        num_values = 0
        for i in range(self._d.size):

            t_p = self._file_temp.variables['temperature'][self._day_idx, i, lat_idx, lon_idx]
            if isinstance(t_p, np.ma.core.MaskedArray):
                t_p = t_p.filled(np.nan)
            temp_pot[i] = t_p
            s = self._file_sal.variables['salinity'][self._day_idx, i, lat_idx, lon_idx]
            if isinstance(s, np.ma.core.MaskedArray):
                s = s.filled(np.nan)
            sal[i] = s
            d[i] = self._d[i]

            if np.isnan(temp_pot[i]) or np.isnan(sal[i]):
                break

            # Calculate in-situ temperature
            p = Oc.d2p(d[i], lat)
            temp_in_situ[i] = Oc.in_situ_temp(s=sal[i], t=temp_pot[i], p=p, pr=self._ref_p)
            # logger.info("%02d: %6.1f (%6.1f) > Tp/Ts/Sal: %3.2f %3.2f %3.2f"
            #             % (i, d[i], p, temp_pot[i], temp_in_situ[i], sal[i]))

            num_values += 1

        if num_values == 0:
            logger.info("no data from lookup!")
            return None

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

    def __repr__(self) -> str:
        msg = "%s" % super(Rtofs, self).__repr__()
        msg += "      <has data loaded: %s>\n" % (self._has_data_loaded,)
        msg += "      <last loaded day: %s>\n" % (self._last_loaded_day.strftime(r"%d\%m\%Y"),)
        return msg
