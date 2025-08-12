import numpy as np
import netCDF4
import os
import re
import calendar
import datetime as dt
import logging

logger = logging.getLogger(__name__)

from hyo2.ssm2 import __version__ as ssp_version
from hyo2.ssm2.lib import __doc__ as ssp_name
from hyo2.ssm2.lib.formats.writers.abstract import AbstractWriter
from hyo2.ssm2.lib.profile.dicts import Dicts


class Ncei(AbstractWriter):
    """NCEI binary writer

    Useful links:
    - http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/profileOrthogonal.cdl
    - http://puma.nerc.ac.uk/cgi-bin/cf-checker.pl
    """

    def __init__(self):
        super(Ncei, self).__init__()
        self.desc = "NCEI"
        self._ext.add('nc')
        self.root_group = None
        self._instrument = None

    @property
    def instrument(self):
        return self._instrument

    @instrument.setter
    def instrument(self, value):
        logger.debug("instrument value: %s" % value)
        self._instrument = value

    def write(self, ssp, data_path, data_file=None, project=''):
        """Writing raw profile data to NetCDF4 file"""
        # logger.debug('*** %s ***: start' % self.driver)

        self.ssp = ssp
        self._project = project

        ship_code = self.ssp.cur.meta.vessel[:2] if len(self.ssp.cur.meta.vessel) >= 2 else 'ZZ'
        nc_file = '%s_%s.nc' % (self.ssp.cur.meta.utc_time.strftime('%Y%m%d%H%M%S'), ship_code)

        # define the output file path
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        file_path = os.path.join(data_path, nc_file)

        self._miss_metadata()
        logger.info("output file: %s" % file_path)

        # create the file
        self.root_group = netCDF4.Dataset(file_path, 'w', format='NETCDF4')

        self._write_header()
        self._write_body()

        self.finalize()

        # logger.debug('*** %s ***: done' % self.driver)
        return True

    def _write_header(self):
        """Write header"""
        # logger.debug('generating header')

        # set the 'z' dimension and the number of profiles (always 1)
        self.root_group.createDimension('z', np.sum(self.ssp.cur.data_valid))
        self.root_group.createDimension('profile', 1)

        # var: profile
        # RECOMMENDED - If using the attribute below: cf_role. Data type can be whatever is appropriate for the
        # unique feature type.
        profile_str = "%s %.7f %.7f" % (self.ssp.cur.meta.utc_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                        self.ssp.cur.meta.longitude, self.ssp.cur.meta.latitude)
        default_profile_str_length = 64
        profile_str_length = max(default_profile_str_length, len(profile_str))
        self.root_group.createDimension('profile_id_length', profile_str_length)
        profile = self.root_group.createVariable('profile', 'S1', ('profile', 'profile_id_length',))
        profile[:] = netCDF4.stringtoarr(profile_str, profile_str_length)
        profile.long_name = 'Unique identifier for each feature instance'  # RECOMMENDED
        profile.cf_role = 'profile_id'  # RECOMMENDED

        # var: time
        # Depending on the precision used for the variable, the data type could be int or double instead of float.
        time = self.root_group.createVariable('time', 'i4', ('profile',), fill_value=0.0)
        time[:] = int(calendar.timegm(self.ssp.cur.meta.utc_time.timetuple()))
        time.long_name = 'cast time'  # RECOMMENDED - Provide a descriptive, long name for this variable.
        time.standard_name = 'time'  # REQUIRED - Do not change
        time.units = 'seconds since 1970-01-01 00:00:00'  # REQUIRED - Use approved CF convention with approved UDUNITS.
        # time.calendar = 'julian'  # REQUIRED    - IF the calendar is not default calendar, which is "gregorian".
        time.axis = 'T'  # REQUIRED    - Do not change.
        # time._FillValue = 0.0  # REQUIRED  if there could be missing values in the data. >> set at var creation
        # time.ancillary_variables = ''  # RECOMMENDED - List other variables providing information about this variable.
        # time.comment = ''  # RECOMMENDED - Add useful, additional information here.

        # var: lat
        # depending on the precision used for the variable, the data type could be int, float or double.
        lat = self.root_group.createVariable('lat', 'f8', ('profile',), fill_value=180.0)
        lat[:] = self.ssp.cur.meta.latitude
        lat.long_name = 'latitude'  # RECOMMENDED - Provide a descriptive, long name for this variable.
        lat.standard_name = 'latitude'  # REQUIRED - Do not change.
        lat.units = 'degrees_north'  # REQUIRED - CF recommends degrees_north, but at least must use UDUNITS.
        lat.axis = 'Y'  # REQUIRED - Do not change.
        lat.valid_min = -90.0  # RECOMMENDED - Replace with correct value.
        lat.valid_max = 180.0  # RECOMMENDED - Replace with correct value.
        # lat._FillValue = 180.0  # REQUIRED if there could be missing values in the data.
        # lat.ancillary_variables = ''  # RECOMMENDED - List other variables providing information about this variable.
        # lat.comment = ''  # RECOMMENDED - Add useful, additional information here.

        # var: lon
        # Depending on the precision used for the variable, the data type could be int, float or double.
        lon = self.root_group.createVariable('lon', 'f8', ('profile',), fill_value=360.0)
        lon[:] = self.ssp.cur.meta.longitude
        lon.long_name = 'longitude'  # RECOMMENDED
        lon.standard_name = 'longitude'  # REQUIRED - This is fixed, do not change.
        lon.units = 'degrees_east'  # REQUIRED - CF recommends degrees_east, but at least use UDUNITS.
        lon.axis = 'X'  # REQUIRED - Do not change.
        lon.valid_min = -180.0  # RECOMMENDED - Replace this with correct value.
        lon.valid_max = 360.0  # RECOMMENDED - Replace this with correct value.
        # lon:_FillValue = 360.0 # REQUIRED if there could be missing values in the data.
        # lon.ancillary_variables = ''  # RECOMMENDED - List other variables providing information about this variable.
        # lon.comment = ''  # RECOMMENDED - Add useful, additional information here.

        # var: crs
        # RECOMMENDED - A container variable storing information about the grid_mapping.
        # All the attributes within a grid_mapping variable are described in:
        # - http://cfconventions.org/Data/cf-conventions/cf-conventions-1.6/build/cf-conventions.html#grid-mappings-
        # and-projections.
        # For all the measurements based on WSG84, the default coordinate system used for GPS measurements,
        # the values shown here should be used.
        crs = self.root_group.createVariable('crs', 'f8', ('profile',))
        crs[:] = 4326.0
        crs.grid_mapping_name = 'latitude_longitude'  # RECOMMENDED
        crs.epsg_code = 'EPSG:4326'  # RECOMMENDED - European Petroleum Survey Group code for the grid mapping name.
        crs.semi_major_axis = 6378137.0  # RECOMMENDED
        crs.inverse_flattening = 298.257223563  # RECOMMENDED

        # global attributes:
        self.root_group.ncei_template_version = 'NCEI_NetCDF_Profile_Orthogonal_Template_v2.0'  # REQUIRED(NCEI)
        self.root_group.featureType = 'profile'  # REQUIRED - CF attribute for identifying the featureType.(CF)
        # SUGGESTED - The data type, as derived from Unidata's Common Data Model Scientific Data types and understood
        # by THREDDS. (ACDD)
        self.root_group.cdm_data_type = 'profile'
        # HIGHLY RECOMMENDED - Provide a useful title for the data in the file.(ACDD)
        self.root_group.title = '%s_%s profile' % (self.ssp.cur.meta.sensor, self.ssp.cur.meta.probe)
        # HIGHLY RECOMMENDED - Provide a useful summary or abstract for the data in the file.(ACDD)
        # self.root_group.summary = ''
        # HIGHLY RECOMMENDED - A comma separated list of keywords coming from the keywords_vocabulary.(ACDD)
        # self.root_group.keywords = ''
        # HIGHLY RECOMMENDED - A comma separated list of the conventions being followed. Always try to use latest
        # version.(CF / ACDD)
        self.root_group.Conventions = 'CF-1.6, ACDD-1.3'
        # RECOMMENDED - Creation date of this version of the data(netCDF).  Use ISO 8601:2004 for date and time. (ACDD)
        self.root_group.date_created = '%s' % dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.root_group.survey = '%s' % self.ssp.cur.meta.survey
        # RECOMMENDED - The name of the project(s) principally responsible for originating this data.
        # Multiple projects can be separated by commas.(ACDD)
        self.root_group.project = '%s' % self._project
        # SUGGESTED - Name of the platform(s) that supported the sensor data used to create this data set or product.
        # Platforms can be of any type, including satellite, ship, station, aircraft or other.(ACDD)
        # Match platform format with velocipy
        platform = str(self.ssp.cur.meta.vessel).upper()
        platform = platform.replace('NRT-', 'NOAA NAVIGATION RESPONSE TEAM-')
        if len(platform) > 2 and platform[:2] in ['RA', 'TJ', 'FH', 'FA']:
            platform = platform.replace('(SHIP)', 'NOAA SHIP')
        self.root_group.platform = '%s' % platform
        # RECOMMENDED -The name of the institution principally responsible for originating this data..  An institution
        # attribute can be used for each variable if variables come from more than one institution. (CF/ACDD)
        self.root_group.institution = '%s' % self.ssp.cur.meta.institution
        # RECOMMENDED - an instrument variable storing information about a parameter of the instrument used in the
        # measurement, the dimensions don't have to be specified if the same instrument is used for all the measurements.
        instrument = self.root_group.createVariable('instrument', 'i4')
        if self._instrument is None:

            instrument.long_name = '%s' % self.ssp.cur.meta.sensor
            probe = str(self.ssp.cur.meta.probe)
            sn = str(self.ssp.cur.meta.sn)
            match = re.match('^(\w+?) ?\(SN:(\w+?)\)', sn)
            if match:
                probe = match.group(1)
                sn = match.group(2)
            instrument.make_model = '%s' % probe
            if self.ssp.cur.meta.sn:
                instrument.serial_number = '%s' % sn

        else:  # this part is used when a custom instrument is passed (for instance, for ISS format)

            tokens = self._instrument.split()
            if len(tokens) > 0:
                instrument.long_name = self._instrument.split()[0]
            if len(tokens) > 1:
                instrument.make_model = self._instrument.split()[1]
            if self.ssp.cur.meta.sn:
                instrument.serial_number = '%s' % self.ssp.cur.meta.sn

        # SUGGESTED - Published or web - based references that describe the data or methods used to produce it.
        # Recommend URIs(such as a URL or DOI)
        self.root_group.references = 'https://www.hydroffice.org/soundspeed/'
        # RECOMMENDED - Provide useful additional information here.(CF)
        # self.root_group.comment = b'Created using HydrOffice %s v.%s' % (ssp_name, ssp_version)
        # SUGGESTED - Version identifier of the data file or product as assigned by the data creator. (ACDD)
        self.root_group.product_version = 'Created using HydrOffice %s v.%s' % (ssp_name, ssp_version)

    def _write_body(self):
        # logger.debug('generating body')

        # valid indices
        vi = self.ssp.cur.data_valid

        # var: depth
        if self._not_empty(self.ssp.cur.data.depth[vi]):
            depth = self.root_group.createVariable('depth', 'f4', ('profile', 'z',))
            depth[:] = self.ssp.cur.data.depth[vi]
            # RECOMMENDED - Provide a descriptive, long name for this variable.
            depth.long_name = 'depth in sea water'
            # REQUIRED - If using a CF standard name and a suitable name exists in the CF standard name table.
            depth.standard_name = 'depth'
            depth.units = 'm'
            depth.axis = 'Z'
            depth.positive = 'down'

        # var: pressure
        if self._not_empty(self.ssp.cur.data.pressure[vi]):
            pressure = self.root_group.createVariable('pressure', 'f4', ('profile', 'z',))
            pressure[:] = self.ssp.cur.data.pressure[vi]
            # RECOMMENDED - Provide a descriptive, long name for this variable.
            pressure.long_name = 'pressure in sea water'
            # REQUIRED - If using a CF standard name and a suitable name exists in the CF standard name table.
            pressure.standard_name = 'sea_water_pressure'
            pressure.units = 'dbar'

        # var: temperature
        if self._not_empty(self.ssp.cur.data.temp[vi]):
            temperature = self.root_group.createVariable('temperature', 'f4', ('profile', 'z',))
            temperature[:] = self.ssp.cur.data.temp[vi]
            # RECOMMENDED - Provide a descriptive, long name for this variable.
            temperature.long_name = 'temperature in sea water'
            # REQUIRED - If using a CF standard name and a suitable name exists in the CF standard name table.
            temperature.standard_name = 'sea_water_temperature'
            temperature.units = 'degree_C'  # REQUIRED - Use UDUNITS compatible units.

        # var: salinity
        if self._not_empty(self.ssp.cur.data.sal[vi]):
            salinity = self.root_group.createVariable('salinity', 'f4', ('profile', 'z',))
            salinity[:] = self.ssp.cur.data.sal[vi]
            # RECOMMENDED - Provide a descriptive, long name for this variable.
            salinity.long_name = 'salinity in sea water'
            # REQUIRED - If using a CF standard name and a suitable name exists in the CF standard name table.
            salinity.standard_name = 'sea_water_practical_salinity'
            salinity.units = '1e-3'  # REQUIRED - Use UDUNITS compatible units.

        # var: conductivity
        if self._not_empty(self.ssp.cur.data.conductivity[vi]):
            conductivity = self.root_group.createVariable('conductivity', 'f4', ('profile', 'z',))
            conductivity[:] = self.ssp.cur.data.conductivity[vi]
            # RECOMMENDED - Provide a descriptive, long name for this variable.
            conductivity.long_name = 'conductivity in sea water'
            # REQUIRED - If using a CF standard name and a suitable name exists in the CF standard name table.
            conductivity.standard_name = 'sea_water_electrical_conductivity'
            conductivity.units = 'S m-1'

        # var: sound speed
        if self._not_empty(self.ssp.cur.data.speed[vi]):
            sound_speed = self.root_group.createVariable('sound_speed', 'f4', ('profile', 'z',))
            sound_speed[:] = self.ssp.cur.data.speed[vi]
            # RECOMMENDED - Provide a descriptive, long name for this variable.
            sound_speed.long_name = 'sound speed in sea water'
            # REQUIRED - If using a CF standard name and a suitable name exists in the CF standard name table.
            sound_speed.standard_name = 'speed_of_sound_in_sea_water'
            sound_speed.units = 'm s-1'  # REQUIRED - Use UDUNITS compatible units.

        # var: flag
        if True:
            flag = self.root_group.createVariable('flag', 'i4', ('profile', 'z',))
            flag[:] = self.ssp.cur.data.flag[vi]
            # RECOMMENDED - Provide a descriptive, long name for this variable.
            flag.long_name = 'quality flag'
            # REQUIRED - If using a CF standard name and a suitable name exists in the CF standard name table.
            # flag.standard_name = ''
            flag.flag_values = 0, 1
            flag.flag_meanings = 'valid invalid'

        self.root_group.close()

    @staticmethod
    def _is_empty(data):
        return data.min() == data.max()

    @staticmethod
    def _not_empty(data):
        return data.min() != data.max()

    def _miss_metadata(self):
        vi = self.ssp.cur.data_valid
        msg = 'NCEI export error: '

        if self.ssp.cur.meta.sensor_type == Dicts.sensor_types['Unknown'] or \
                self.ssp.cur.meta.sensor_type == Dicts.sensor_types['Synthetic']:
            msg = '%s cannot export from sensor - %s, probe - %s' % (
            msg, self.ssp.cur.meta.sensor, self.ssp.cur.meta.probe)
        elif self._is_empty(self.ssp.cur.data.depth[vi]) and self._is_empty(self.ssp.cur.data.pressure[vi]):
            msg = '%s missing depth or pressure' % msg
        elif self._is_empty(self.ssp.cur.data.speed[vi]) and self._is_empty(self.ssp.cur.data.temp[vi]) and \
                self._is_empty(self.ssp.cur.data.conductivity[vi]) and self._is_empty(self.ssp.cur.data.sal[vi]):
            msg = '%s missing critical data' % msg
        elif self._project in ['', 'default']:
            msg = '%s project name is not valid' % msg
        elif not self.ssp.cur.meta.survey or not self.ssp.cur.meta.vessel or not self.ssp.cur.meta.institution:
            msg = '%s missing survey, vessel, or institution' % msg

        if msg != 'NCEI export error: ':
            raise RuntimeError(msg)
