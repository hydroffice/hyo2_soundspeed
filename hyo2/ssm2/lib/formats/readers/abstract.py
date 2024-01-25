from abc import ABCMeta, abstractmethod
import numpy as np
import logging

from hyo2.ssm2.lib.base.files import FileManager
from hyo2.ssm2.lib.base.callbacks.cli_callbacks import CliCallbacks
from hyo2.ssm2.lib.formats.abstract import AbstractFormat
from hyo2.ssm2.lib.profile.dicts import Dicts

logger = logging.getLogger(__name__)


class AbstractReader(AbstractFormat, metaclass=ABCMeta):
    """ Abstract data reader """

    def __init__(self):
        super(AbstractReader, self).__init__()
        self.fid = None

    def __repr__(self):
        return "<%s:reader:%s:%s>" % (self.name, self.version, ",".join(self.ext))

    @abstractmethod
    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        """Common read function signature

        The settings is a container with all the library settings.
        The callback is a class that collects callback functions.
        """
        pass

    @abstractmethod
    def _parse_header(self):
        pass

    @abstractmethod
    def _parse_body(self):
        pass

    def fix(self):
        """Function called after the parsing is done, to execute some common checks/integration"""

        for profile in self.ssp.l:  # we may have multiple profiles

            if not np.count_nonzero(profile.data.depth) and not np.count_nonzero(profile.data.pressure):
                self.ssp.clear()
                raise RuntimeError("missing both depth and pressure values")

            # check if location is present
            if (profile.meta.latitude is None) or (profile.meta.longitude is None):

                profile.meta.latitude, profile.meta.longitude = self.cb.ask_location()
                if (profile.meta.latitude is None) or (profile.meta.longitude is None):
                    self.ssp.clear()
                    raise RuntimeError("missing geographic location required for database lookup")

            # check if location is an reasonable number present
            elif (abs(profile.meta.latitude) > 90.0) or (abs(profile.meta.longitude) > 360.0):
                logger.info('The retrieved location values does not look correct: (%f, %f) -> ASK USER'
                            % (profile.meta.longitude, profile.meta.latitude))

                profile.meta.latitude, profile.meta.longitude = self.cb.ask_location()
                if (profile.meta.latitude is None) or (profile.meta.longitude is None):
                    self.ssp.clear()
                    raise RuntimeError("missing geographic location required for database lookup")

            # Calc salinity if conductivity and temperature
            if not np.count_nonzero(profile.data.sal) and \
                    np.count_nonzero(profile.data.conductivity) and \
                    np.count_nonzero(profile.data.temp):
                profile.calc_salinity_from_conductivity()

            # Calc salinity if sound speed and temperature for SVP and SVPT sensor types
            if self.ssp.cur.meta.sensor_type in [Dicts.sensor_types["SVP"], Dicts.sensor_types["SVPT"]]:
                if not np.count_nonzero(self.ssp.cur.data.sal) and \
                        np.count_nonzero(self.ssp.cur.data.temp) and \
                        np.count_nonzero(self.ssp.cur.data.speed):
                    self.ssp.cur.calc_salinity_from_speed_and_temp()

            # Calc depth data if needed since we are now guaranteed a lat/lon
            if not np.count_nonzero(profile.data.depth) and \
                    np.count_nonzero(profile.data.pressure):
                # first select samples by casting direction but using pressure
                profile.reduce_up_down(self.s.ssp_up_or_down, use_pressure=True)

                profile.calc_data_depth()

            else:
                # select samples by casting direction
                profile.reduce_up_down(self.s.ssp_up_or_down, use_pressure=False)

            # Calc speed if needed (must have temp+salinity) since we are now guaranteed depth.
            if not np.count_nonzero(profile.data.speed) and \
                    np.count_nonzero(profile.data.temp) and \
                    np.count_nonzero(profile.data.sal):
                profile.calc_data_speed()

            # check if timestamp is present
            if profile.meta.utc_time is None:
                profile.meta.utc_time = self.cb.ask_date()
                if profile.meta.utc_time is None:
                    self.ssp.clear()
                    raise RuntimeError("missing date required for database lookup")

            # check for default metadata
            if self.s.auto_apply_default_metadata:
                if len(profile.meta.institution) == 0:
                    if len(self.s.default_institution) != 0:
                        profile.meta.institution = self.s.default_institution
                        # logger.debug('default institution: %s' % profile.meta.institution)
                if len(profile.meta.survey) == 0:
                    if len(self.s.default_survey) != 0:
                        profile.meta.survey = self.s.default_survey
                        # logger.debug('default survey: %s' % profile.meta.survey)
                if len(profile.meta.vessel) == 0:
                    if len(self.s.default_vessel) != 0:
                        profile.meta.vessel = self.s.default_vessel
                        # logger.debug('default vessel: %s' % profile.meta.vessel)

    def finalize(self):
        """Function called at the end, to finalize the reading (e.g., clone raw to proc)"""

        for profile in self.ssp.l:  # we may have multiple profiles
            profile.clone_data_to_proc()
            profile.init_sis()  # initialize to zero


class AbstractTextReader(AbstractReader, metaclass=ABCMeta):
    """ Abstract text data reader """

    def __init__(self):
        super(AbstractTextReader, self).__init__()
        self.lines = []
        self.total_data = None
        self.samples_offset = None

    def _read(self, data_path, encoding='utf8'):
        """Helper function to read the raw file"""
        self.fid = FileManager(data_path, mode='r', encoding=encoding)
        try:
            self.total_data = self.fid.io.read()
            self.lines = self.total_data.splitlines()
        except UnicodeDecodeError as e:
            if encoding == 'utf8':
                logger.info("changing encoding to latin: %s" % e)
                self.fid = FileManager(data_path, mode='r', encoding='latin')
                self.total_data = self.fid.io.read()
                self.lines = self.total_data.splitlines()
            elif encoding == 'latin':
                logger.info("changing encoding to utf8: %s" % e)
                self.fid = FileManager(data_path, mode='r', encoding='utf8')
                self.total_data = self.fid.io.read()
                self.lines = self.total_data.splitlines()
            else:
                raise e
        self.samples_offset = 0
        self.field_index = dict()
        self.more_fields = list()

        if self.fid is not None:
            self.fid.close()


class AbstractBinaryReader(AbstractReader, metaclass=ABCMeta):
    """ Abstract binary data reader """

    def __init__(self):
        super(AbstractBinaryReader, self).__init__()

    def _read(self, data_path):
        """Helper function to read the raw file"""
        self.fid = FileManager(data_path, mode='rb')
