import time
import os
import re
import copy
import shutil
import traceback
import logging
from typing import Optional, TYPE_CHECKING
from appdirs import user_data_dir

from hyo2.abc.lib.progress.abstract_progress import AbstractProgress
from hyo2.abc.lib.progress.cli_progress import CliProgress
from hyo2.abc.lib.gdal_aux import GdalAux
from hyo2.abc.lib.helper import Helper

from hyo2.soundspeed import lib_info
from hyo2.soundspeed import formats
from hyo2.soundspeed.atlas.atlases import Atlases
from hyo2.soundspeed.base.callbacks.abstract_callbacks import AbstractCallbacks
from hyo2.soundspeed.base.callbacks.cli_callbacks import CliCallbacks
from hyo2.soundspeed.base.setup import Setup
from hyo2.soundspeed.db.db import ProjectDb
from hyo2.soundspeed.listener.listeners import Listeners
from hyo2.soundspeed.logger.sqlitelogging import SqliteLogging
from hyo2.soundspeed.profile.profilelist import ProfileList
from hyo2.soundspeed.profile.dicts import Dicts
from hyo2.soundspeed.server.server import Server
from hyo2.soundspeed.profile.ray_tracing.tracedprofile import TracedProfile
from hyo2.soundspeed.profile.ray_tracing.diff_tracedprofiles import DiffTracedProfiles
from hyo2.soundspeed.profile.ray_tracing.plot_tracedprofiles import PlotTracedProfiles

if TYPE_CHECKING:
    from datetime import datetime
    from hyo2.soundspeed.profile.profile import Profile
    from hyo2.soundspeed.db.export import ExportDbFields


logger = logging.getLogger(__name__)


class SoundSpeedLibrary:
    """Sound Speed library"""

    def __init__(self, data_folder: Optional[str] = None,
                 callbacks: AbstractCallbacks = CliCallbacks(), progress: AbstractProgress = CliProgress()) -> None:
        """Initialization for the library"""
        # logger.info("** > LIB: initializing ...")

        # callbacks
        self.cb = callbacks
        # progress bar
        self.progress = progress

        self.ssp = None  # current profile
        self.ref = None  # reference profile

        # take care of all the required folders
        self._data_folder = None
        self._releases_folder = None
        self._release_folder = None
        self._projects_folder = None
        self._outputs_folder = None
        # _noaa_project format OPR-Xnnn-XX-nn
        self._noaa_project = None
        self._noaa_project_validate = re.compile(r"^(OPR-[A-Z]\d{3}-[A-Z]{2}-\d{2})")
        self.set_folders(data_folder=data_folder)

        # load settings and other functionalities
        self.setup = Setup(release_folder=self.release_folder)
        self.atlases = Atlases(prj=self)
        self.check_custom_folders()
        self.listeners = Listeners(prj=self)
        self.cb.sis_listener = self.listeners.sis4  # to provide default values from SIS4 (if available)
        self.cb.kctrl_listener = self.listeners.sis5  # to provide default values from SIS5 (if available)
        self.server = Server(prj=self)
        self.logs = SqliteLogging(self._release_folder)  # (user and server) loggers

        self.logging()  # Set on/off logging for user and server based on loaded settings

        # logger.info("** > LIB: initialized!")

    def check_custom_folders(self) -> None:
        # logger.info("Checking for custom folders")

        # projects folder
        if len(self.setup.custom_projects_folder):

            if os.path.exists(self.setup.custom_projects_folder):
                self._projects_folder = self.setup.custom_projects_folder
            else:  # delete the not-existing folder
                self.setup.custom_projects_folder = str()
                self.setup.save_to_db()

        # outputs folder
        if len(self.setup.custom_outputs_folder):

            if os.path.exists(self.setup.custom_outputs_folder):
                self._outputs_folder = self.setup.custom_outputs_folder
            else:  # delete the not-existing folder
                self.setup.custom_outputs_folder = str()
                self.setup.save_to_db()

    def close(self) -> None:
        """Destructor"""
        logger.info("** > LIB: closing ...")

        self.listeners.stop()

        if self.server.is_alive():
            self.server.stop()
            self.server.join(2)

        logger.info("** > LIB: closed!")

    # --- library, release, atlases, and projects folders

    @classmethod
    def make_data_folder(cls, data_folder: Optional[str] = None) -> str:

        # output data folder: where all the library data are written
        if data_folder is None:
            data_folder = user_data_dir(lib_info.lib_name, "HydrOffice")
        if not os.path.exists(data_folder):  # create it if it does not exist
            os.makedirs(data_folder)
        # logger.debug("library folder: %s" % data_folder)
        return data_folder

    @classmethod
    def make_releases_folder(cls, data_folder: Optional[str] = None) -> str:

        data_folder = cls.make_data_folder(data_folder=data_folder)

        # releases data folder
        releases_folder = os.path.join(data_folder, "releases")
        if not os.path.exists(releases_folder):  # create it if it does not exist
            os.makedirs(releases_folder)
        # logger.debug("releases folder: %s" % self.releases_folder)

        return releases_folder

    @classmethod
    def make_release_folder(cls, data_folder: Optional[str] = None) -> str:
        # release data folder: release-specific data (as settings)
        releases_folder = cls.make_releases_folder(data_folder=data_folder)
        release_folder = os.path.join(releases_folder, lib_info.lib_version[:lib_info.lib_version.rindex('.')])
        if not os.path.exists(release_folder):  # create it if it does not exist
            os.makedirs(release_folder)
        # logger.debug("release folder: %s" % self.release_folder)

        return release_folder

    @classmethod
    def setup_path(cls) -> str:
        release_folder = cls.make_release_folder()
        return os.path.join(release_folder, "setup.db")

    @classmethod
    def setup_exists(cls) -> bool:
        return os.path.exists(cls.setup_path())

    @classmethod
    def list_other_setups(cls) -> list:
        releases_folder = cls.make_releases_folder()
        old_setups = list()
        for release in os.listdir(releases_folder):

            release_path = os.path.join(releases_folder, release)
            setup_path = os.path.join(release_path, "setup.db")

            if not os.path.exists(setup_path):
                continue

            # if exists, attempt to load the setup
            try:
                Setup(release_folder=release_path)
            except Exception as e:
                logger.debug("skipping %s: %s" % (release_path, e))
                continue

            logger.debug("found setup: %s" % setup_path)
            old_setups.append(setup_path)

        return old_setups

    @classmethod
    def copy_setup(cls, input_setup: str) -> bool:
        from shutil import copyfile
        release_folder = cls.make_release_folder()
        output_setup = os.path.join(release_folder, "setup.db")
        copyfile(input_setup, output_setup)
        updates_required = Setup.are_updates_required(output_setup)
        logger.debug("updates required: %s" % updates_required)
        if updates_required:
            success = Setup.apply_required_updates(output_setup)
            if not success:
                os.remove(output_setup)
                return False
        logger.info("copied content from: %s to: %s" % (input_setup, output_setup))
        return True

    def set_folders(self, data_folder: str) -> None:
        """manage library folders creation"""

        self._data_folder = self.make_data_folder(data_folder=data_folder)
        self._releases_folder = self.make_releases_folder(data_folder=data_folder)
        self._release_folder = self.make_release_folder(data_folder=data_folder)

        # projects folder
        self._projects_folder = os.path.join(self.data_folder, "projects")
        if not os.path.exists(self._projects_folder):  # create it if it does not exist
            os.makedirs(self._projects_folder)
        # logger.debug("projects folder: %s" % self.projects_folder)

        # outputs folder
        self._outputs_folder = os.path.join(self.data_folder, "outputs")
        if not os.path.exists(self._outputs_folder):  # create it if it does not exist
            os.makedirs(self._outputs_folder)
            # logger.debug("outputs folder: %s" % self.projects_folder)

    # library data folder

    @property
    def data_folder(self) -> str:
        """Get the library data folder"""
        return self._data_folder

    @data_folder.setter
    def data_folder(self, value: str) -> None:
        """ Set the library data folder"""
        self._data_folder = value

    def open_data_folder(self) -> None:
        Helper.explore_folder(self.data_folder)

    # releases folder

    @property
    def releases_folder(self) -> str:
        """Get the releases data folder"""
        return self._releases_folder

    @releases_folder.setter
    def releases_folder(self, value: str) -> None:
        """ Set the releases data folder"""
        self._releases_folder = value

    def open_releases_folder(self) -> None:
        Helper.explore_folder(self.releases_folder)

    # release folder

    @property
    def release_folder(self) -> str:
        """Get the release data folder"""
        return self._release_folder

    @release_folder.setter
    def release_folder(self, value: str) -> None:
        """ Set the release data folder"""
        self._release_folder = value

    # atlases

    @property
    def atlases_folder(self) -> str:
        """Get the atlases folder"""
        return self.atlases.atlases_folder

    def open_atlases_folder(self) -> None:
        Helper.explore_folder(self.atlases_folder)

    @property
    def woa09_folder(self) -> str:
        """Get the woa09 atlas folder"""
        return self.atlases.woa09_folder

    @property
    def woa13_folder(self) -> str:
        """Get the woa13 atlas folder"""
        return self.atlases.woa13_folder

    @property
    def rtofs_folder(self) -> str:
        """Get the rtofs atlas folder"""
        return self.atlases.rtofs_folder

    @property
    def regofs_folder(self) -> str:
        """Get the regofs atlas folder"""
        return self.atlases.regofs_folder

    # projects

    @property
    def projects_folder(self) -> str:
        """Get the projects folder"""
        return self._projects_folder

    @projects_folder.setter
    def projects_folder(self, value: str) -> None:
        """ Set the projects folder"""
        self._projects_folder = value

    def open_projects_folder(self) -> None:
        Helper.explore_folder(self.projects_folder)

    # outputs

    @property
    def outputs_folder(self) -> str:
        """Get the outputs folder"""
        return self._outputs_folder

    @outputs_folder.setter
    def outputs_folder(self, value: str) -> None:
        """ Set the outputs folder"""
        self._outputs_folder = value

    def open_outputs_folder(self) -> None:
        Helper.explore_folder(self.outputs_folder)

    # --- readers/writers

    @property
    def readers(self) -> list:
        return formats.readers

    @property
    def name_readers(self) -> list:
        return formats.name_readers

    @property
    def ext_readers(self) -> list:
        return formats.ext_readers

    @property
    def desc_readers(self) -> list:
        return formats.desc_readers

    @property
    def writers(self) -> list:
        return formats.writers

    @property
    def name_writers(self) -> list:
        return formats.name_writers

    @property
    def ext_writers(self) -> list:
        return formats.ext_writers

    @property
    def desc_writers(self) -> list:
        return formats.desc_writers

    # --- sqlite logging

    def has_active_user_logger(self) -> bool:
        return self.logs.user_active

    def activate_user_logger(self, flag: bool) -> None:
        if flag:
            self.logs.activate_user_db()
        else:
            self.logs.deactivate_user_db()

    def has_active_server_logger(self) -> bool:
        return self.logs.server_active

    def activate_server_logger(self, flag: bool) -> None:
        if flag:
            self.logs.activate_server_db()
        else:
            self.logs.deactivate_server_db()

    # --- ssp profile

    @property
    def ssp_list(self) -> ProfileList:
        return self.ssp

    @property
    def cur(self) -> Optional['Profile']:
        if self.ssp is None:
            return None
        return self.ssp.cur

    @property
    def cur_basename(self) -> str:
        if self.cur is None:
            return "output"
        if self.cur.meta.original_path is None:
            return "output"
        # noinspection PyTypeChecker
        return os.path.basename(self.cur.meta.original_path).split('.')[0]

    @property
    def cur_file(self) -> Optional[str]:
        if self.cur is None:
            return None
        if self.cur.meta.original_path is None:
            return None
        return os.path.basename(self.cur.meta.original_path)

    def has_ssp(self) -> bool:
        if self.cur is None:
            return False
        return True

    def has_ref(self) -> bool:
        if self.ref is None:
            return False
        return True

    # --- listeners

    def has_mvp_to_process(self) -> bool:
        if not self.use_mvp():
            return False

        return self.listeners.mvp_to_process

    def has_sippican_to_process(self) -> bool:
        if not self.use_sippican():
            return False

        return self.listeners.sippican_to_process

    # --- import data

    def import_data(self, data_path: str, data_format: str, skip_atlas: bool = False) -> None:
        """Import data using a specific format name"""

        # identify reader to use
        idx = self.name_readers.index(data_format)
        reader = self.readers[idx]
        logger.debug("%s > path: %s" % (data_format, data_path))

        # call the reader to process the data file
        success = reader.read(data_path=data_path, settings=self.setup, callbacks=self.cb, progress=self.progress)
        if not success:
            raise RuntimeError("Error using %s reader for file: %s"
                               % (reader.desc, data_path))
        self.ssp = reader.ssp
        logger.debug("data file successfully parsed!")

        if not skip_atlas:
            self._retrieve_atlases()

    def create_profile(self, start_depth, start_temp, start_sal, start_speed,
                       end_depth, end_temp, end_sal, end_speed):

        ssp = ProfileList()
        ssp.append()  # append a new profile
        # initialize probe/sensor type
        ssp.cur.meta.sensor_type = Dicts.sensor_types['Synthetic']
        ssp.cur.meta.probe_type = Dicts.probe_types['Unknown']

        ssp.cur.meta.latitude, ssp.cur.meta.longitude = self.cb.ask_location()
        if (ssp.cur.meta.latitude is None) or (ssp.cur.meta.longitude is None):
            ssp.clear()
            raise RuntimeError("missing geographic location required for database lookup")

        ssp.cur.meta.utc_time = self.cb.ask_date()
        if ssp.cur.meta.utc_time is None:
            ssp.clear()
            raise RuntimeError("missing date required for database lookup")

        ssp.cur.init_data(2)

        ssp.cur.data.depth[0] = start_depth
        ssp.cur.data.temp[0] = start_temp
        ssp.cur.data.sal[0] = start_sal
        ssp.cur.data.speed[0] = start_speed

        ssp.cur.data.depth[1] = end_depth
        ssp.cur.data.temp[1] = end_temp
        ssp.cur.data.sal[1] = end_sal
        ssp.cur.data.speed[1] = end_speed

        ssp.cur.clone_data_to_proc()
        ssp.cur.init_sis()  # initialize to zero

        self.ssp = ssp

        self._retrieve_atlases()

    def _retrieve_atlases(self):
        # retrieve atlases data for each retrieved profile
        for pr in self.ssp.l:

            if self.use_woa09() and self.has_woa09():
                pr.woa09 = self.atlases.woa09.query(lat=pr.meta.latitude, lon=pr.meta.longitude,
                                                    dtstamp=pr.meta.utc_time)

            if self.use_woa13() and self.has_woa13():
                pr.woa13 = self.atlases.woa13.query(lat=pr.meta.latitude, lon=pr.meta.longitude,
                                                    dtstamp=pr.meta.utc_time)

            if self.use_rtofs():
                # noinspection PyBroadException
                try:
                    pr.rtofs = self.atlases.rtofs.query(lat=pr.meta.latitude, lon=pr.meta.longitude,
                                                        dtstamp=pr.meta.utc_time)
                except Exception:
                    pr.rtofs = None
                    logger.warning("unable to retrieve RTOFS data")

            if self.use_gomofs():
                # noinspection PyBroadException
                try:
                    pr.gomofs = self.atlases.gomofs.query(lat=pr.meta.latitude, lon=pr.meta.longitude,
                                                          dtstamp=pr.meta.utc_time)
                except Exception:
                    pr.gomofs = None
                    logger.warning("unable to retrieve GOMOFS data")

    # --- receive data

    def retrieve_woa09(self) -> None:
        """Retrieve data from WOA09 atlas"""

        if not self.has_woa09():
            logger.error("missing WOA09 atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        self.ssp = self.atlases.woa09.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_woa13(self) -> None:
        """Retrieve data from WOA13 atlas"""

        if not self.has_woa13():
            logger.error("missing WOA13 atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        self.ssp = self.atlases.woa13.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_rtofs(self) -> None:
        """Retrieve data from RTOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_rtofs(datestamp=utc_time):
            logger.error("unable to download RTOFS atlas data set")
            return

        if not self.has_rtofs():
            logger.error("missing RTOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.rtofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_gomofs(self) -> None:
        """Retrieve data from GoMOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_gomofs(datestamp=utc_time):
            logger.error("unable to download GoMOFS atlas data set")
            return

        if not self.has_gomofs():
            logger.error("missing GoMOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.gomofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_leofs(self) -> None:
        """Retrieve data from LEOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_leofs(datestamp=utc_time):
            logger.error("unable to download LEOFS atlas data set")
            return

        if not self.has_leofs():
            logger.error("missing LEOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.leofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_cbofs(self) -> None:
        """Retrieve data from CBOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_cbofs(datestamp=utc_time):
            logger.error("unable to download CBOFS atlas data set")
            return

        if not self.has_cbofs():
            logger.error("missing CBOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.cbofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_dbofs(self) -> None:
        """Retrieve data from DBOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_dbofs(datestamp=utc_time):
            logger.error("unable to download DBOFS atlas data set")
            return

        if not self.has_dbofs():
            logger.error("missing DBOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.dbofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_ngofs(self) -> None:
        """Retrieve data from NGOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_ngofs(datestamp=utc_time):
            logger.error("unable to download NGOFS atlas data set")
            return

        if not self.has_ngofs():
            logger.error("missing NGOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.ngofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_tbofs(self) -> None:
        """Retrieve data from TBOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_tbofs(datestamp=utc_time):
            logger.error("unable to download TBOFS atlas data set")
            return

        if not self.has_tbofs():
            logger.error("missing TBOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.tbofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_creofs(self) -> None:
        """Retrieve data from CREOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_creofs(datestamp=utc_time):
            logger.error("unable to download CREOFS atlas data set")
            return

        if not self.has_creofs():
            logger.error("missing CREOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.creofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_sfbofs(self) -> None:
        """Retrieve data from SFBOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_sfbofs(datestamp=utc_time):
            logger.error("unable to download SFBOFS atlas data set")
            return

        if not self.has_sfbofs():
            logger.error("missing SFBOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.sfbofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_nyofs(self) -> None:
        """Retrieve data from NYOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_nyofs(datestamp=utc_time):
            logger.error("unable to download NYOFS atlas data set")
            return

        if not self.has_nyofs():
            logger.error("missing NYOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.nyofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_sjrofs(self) -> None:
        """Retrieve data from SJROFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_sjrofs(datestamp=utc_time):
            logger.error("unable to download SJROFS atlas data set")
            return

        if not self.has_ngofs():
            logger.error("missing SJROFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.sjrofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_lhofs(self) -> None:
        """Retrieve data from LHOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_lhofs(datestamp=utc_time):
            logger.error("unable to download LHOFS atlas data set")
            return

        if not self.has_lhofs():
            logger.error("missing LHOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.lhofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_lmofs(self) -> None:
        """Retrieve data from LMOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_lmofs(datestamp=utc_time):
            logger.error("unable to download LMOFS atlas data set")
            return

        if not self.has_lmofs():
            logger.error("missing LMOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.lmofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_loofs(self) -> None:
        """Retrieve data from LOOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_loofs(datestamp=utc_time):
            logger.error("unable to download LOOFS atlas data set")
            return

        if not self.has_loofs():
            logger.error("missing LOOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.loofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_lsofs(self) -> None:
        """Retrieve data from LSOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return

        if not self.download_lsofs(datestamp=utc_time):
            logger.error("unable to download LSOFS atlas data set")
            return

        if not self.has_lsofs():
            logger.error("missing LSOFS atlas data set")
            return

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return

        self.ssp = self.atlases.lsofs.query(lat=lat, lon=lon, dtstamp=utc_time)

    def retrieve_sis4(self) -> None:
        """Retrieve data from SIS4"""
        if not self.use_sis4():
            raise RuntimeError("use SIS4 option is disabled")

        self.progress.start(text="Retrieve from SIS4")

        if not self.listen_sis4():
            raise RuntimeError("unable to listen SIS4")

        prog_quantum = 50 / len(self.setup.client_list.clients)

        for client in self.setup.client_list.clients:
            client.request_profile_from_sis4(prj=self)
            self.progress.add(prog_quantum)

        if not self.listeners.sis4.ssp:
            self.progress.end()
            raise RuntimeError("Unable to get SIS4 cast from any clients")

        # logger.info("got SSP from SIS4: %s" % self.listeners.sis4.ssp)
        self.progress.update(80)

        # try to retrieve the location from SIS4
        lat = None
        lon = None
        if self.listeners.sis4.nav:
            from_sis = self.cb.ask_location_from_sis()
            if from_sis:
                lat, lon = self.listeners.sis4.nav.latitude, self.listeners.sis4.nav.longitude
        # if we don't have a location, ask user
        if (lat is None) or (lon is None):
            lat, lon = self.cb.ask_location()
            if (lat is None) or (lon is None):
                self.progress.end()
                raise RuntimeError("missing geographic location required for database lookup")

        ssp = self.listeners.sis4.ssp.convert_ssp()
        ssp.meta.latitude = lat
        ssp.meta.longitude = lon
        ssp.clone_data_to_proc()
        ssp.init_sis()  # initialize to zero
        ssp_list = ProfileList()
        ssp_list.append_profile(ssp)
        self.ssp = ssp_list
        self.progress.end()

    def retrieve_sis5(self) -> None:
        """Retrieve data from SIS5"""
        if not self.use_sis5():
            raise RuntimeError("use SIS5 option is disabled")

        self.progress.start(text="Retrieve from SIS5")

        if not self.listen_sis5():
            raise RuntimeError("unable to listen SIS5")

        prog_quantum = 50 / len(self.setup.client_list.clients)

        for client in self.setup.client_list.clients:
            client.request_profile_from_sis5(prj=self)
            self.progress.add(prog_quantum)

        if not self.listeners.sis5.svp:
            self.progress.end()
            raise RuntimeError("Unable to get SIS5 cast from any clients")

        # logger.info("got SSP from SIS5: %s" % self.listeners.sis5.svp)
        self.progress.update(80)

        # try to retrieve the location from SIS5
        lat = None
        lon = None
        if self.listeners.sis5.spo:
            from_sis = self.cb.ask_location_from_sis()
            if from_sis:
                lat, lon = self.listeners.sis5.spo.latitude, self.listeners.sis5.spo.longitude
        # if we don't have a location, ask user
        if (lat is None) or (lon is None):
            lat, lon = self.cb.ask_location()
            if (lat is None) or (lon is None):
                self.progress.end()
                raise RuntimeError("missing geographic location required for database lookup")

        ssp = self.listeners.sis5.svp.convert_ssp()
        ssp.meta.latitude = lat
        ssp.meta.longitude = lon
        ssp.clone_data_to_proc()
        ssp.init_sis()  # initialize to zero
        ssp_list = ProfileList()
        ssp_list.append_profile(ssp)
        self.ssp = ssp_list
        self.progress.end()

    # --- export data

    def export_data(self, data_formats: list, data_paths: Optional[dict],
                    data_files: Optional[dict] = None, custom_writer_instrument: Optional[str] = None):
        """Export data using a list of formats name"""

        # checks
        if not self.has_ssp():
            raise RuntimeError("Data not loaded")

        has_data_files = False
        if data_files is not None:
            if len(data_files) == 0:
                has_data_files = False
            elif len(data_formats) != len(data_files):
                raise RuntimeError("Mismatch between format and file lists")
            else:
                has_data_files = True

        if data_paths is None:
            data_paths = dict()
            for name in data_formats:
                data_paths[name] = self.outputs_folder

        # create the outputs
        for i, name in enumerate(data_formats):

            # special case: synthetic multiple profiles, we just save the average profile
            if (name == 'ncei') and (self.ssp.l[0].meta.sensor_type == Dicts.sensor_types['Synthetic']):
                raise RuntimeError("Attempt to export a synthetic profile in NCEI format!")

            idx = self.name_writers.index(name)
            writer = self.writers[idx]

            # special case for Kongsberg asvp format
            if name == 'asvp':

                tolerances = [0.01, 0.03, 0.06, 0.1, 0.5]
                for tolerance in tolerances:

                    if not self.prepare_sis(thin_tolerance=tolerance):
                        logger.warning("issue in preparing the data for SIS")
                        return False

                    si = self.cur.sis_thinned
                    thin_profile_length = self.cur.sis.flag[si].size
                    logger.debug("thin profile size: %d (with tolerance: %.3f)" % (thin_profile_length, tolerance))
                    if thin_profile_length < 1000:
                        break

                    logger.info("too many samples, attempting with a lower tolerance")

            # special case (currently only used for Fugro ISS)
            if name == 'ncei':
                if custom_writer_instrument is not None:
                    logger.debug("NCEI custom writer instrument: %s" % custom_writer_instrument)
                    writer.instrument = custom_writer_instrument

            current_project = self.current_project
            if name == 'ncei' and self.setup.noaa_tools:
                current_project = self.noaa_project

            if not has_data_files:  # we don't have the output file names
                writer.write(ssp=self.ssp, data_path=data_paths[name], project=current_project)
            else:
                writer.write(ssp=self.ssp, data_path=data_paths[name], data_file=data_files[name],
                             project=current_project)

        # take care of listeners
        if self.has_sippican_to_process():
            self.listeners.sippican_to_process = False
        if self.has_mvp_to_process():
            self.listeners.mvp_to_process = False

    # --- project db

    @property
    def noaa_project(self) -> str:
        """temporary NOAA project name for NCEI"""
        return str(self._noaa_project)

    def not_noaa_project(self, value: str, format_ok: bool = False) -> bool:
        # noinspection PyBroadException
        try:
            self._noaa_project = self._noaa_project_validate.match(value).group(1)
            return False

        except Exception:
            if format_ok:
                self._noaa_project = value
                return False
            else:
                return True

    @property
    def current_project(self) -> str:
        return self.setup.current_project

    @current_project.setter
    def current_project(self, value: str) -> None:
        self.setup.current_project = value

    def rename_current_project(self, name: str) -> None:
        old_db_path = os.path.join(self.projects_folder, self.current_project + ".db")
        if not os.path.exists(old_db_path):
            raise RuntimeError("unable to locate the current project: %s" % old_db_path)

        new_db_path = os.path.join(self.projects_folder, name + ".db")
        if os.path.exists(new_db_path):
            raise RuntimeError("the project already exists: %s" % new_db_path)

        shutil.copy(old_db_path, new_db_path)
        if not os.path.exists(new_db_path):
            raise RuntimeError("unable to copy the project db: %s" % new_db_path)

        self.setup.current_project = name
        self.save_settings_to_db()
        self.reload_settings_from_db()

        os.remove(old_db_path)

    def remove_project(self, name: str) -> None:
        if name == self.current_project:
            raise RuntimeError("unable to remove the current project: %s" % self.current_project)

        db_path = os.path.join(self.projects_folder, name + ".db")
        if not os.path.exists(db_path):
            raise RuntimeError("unable to locate the project to delete: %s" % db_path)

        os.remove(db_path)

    def list_projects(self) -> list:
        """Return a list with all the available projects"""
        prj_list = list()
        for root, dirs, files in os.walk(self.projects_folder):
            for f in files:
                if "thumbs" in f.lower():
                    continue
                if f.endswith('.db'):
                    prj_list.append(os.path.splitext(os.path.basename(f))[0])
            break
        return prj_list

    def remove_data(self) -> bool:
        """Remove the current profile in the project db"""

        # checks
        if not self.has_ssp():
            raise RuntimeError("Data not loaded")

        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)

        # special case: synthetic multiple profiles, we just save the average profile
        if (self.ssp.l[0].meta.sensor_type == Dicts.sensor_types['Synthetic']) and \
                ((self.ssp.l[0].meta.probe_type == Dicts.probe_types['WOA09']) or
                 (self.ssp.l[0].meta.probe_type == Dicts.probe_types['WOA13'])):
            tmp_ssp = copy.deepcopy(self.ssp)
            del tmp_ssp.l[1:]
            success = db.remove_casts(tmp_ssp)

        else:
            success = db.remove_casts(self.ssp)
        db.disconnect()

        # take care of listeners
        if success:
            if self.has_sippican_to_process():
                self.listeners.sippican_to_process = False
            if self.has_mvp_to_process():
                self.listeners.mvp_to_process = False

        return success

    def store_data(self) -> bool:
        """Store the current profile in the project db"""

        # checks
        if not self.has_ssp():
            raise RuntimeError("Data not loaded")

        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)

        # special case: synthetic multiple profiles, we just save the average profile
        if (self.ssp.l[0].meta.sensor_type == Dicts.sensor_types['Synthetic']) and \
                ((self.ssp.l[0].meta.probe_type == Dicts.probe_types['WOA09']) or
                 (self.ssp.l[0].meta.probe_type == Dicts.probe_types['WOA13'])):
            tmp_ssp = copy.deepcopy(self.ssp)
            del tmp_ssp.l[1:]
            success = db.add_casts(tmp_ssp)

        else:
            success = db.add_casts(self.ssp)
        db.disconnect()

        # take care of listeners
        if success:
            if self.has_sippican_to_process():
                self.listeners.sippican_to_process = False
            if self.has_mvp_to_process():
                self.listeners.mvp_to_process = False

        return success

    def db_list_profiles(self, project: Optional[str] = None) -> list:
        """List the profile on the db"""
        if project is None:
            project = self.current_project

        db = ProjectDb(projects_folder=self.projects_folder, project_name=project)
        lst = db.list_profiles()
        db.disconnect()
        return lst

    def db_retrieve_profile(self, pk: int) -> ProfileList:
        """Retrieve a profile by primary key"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        ssp = db.profile_by_pk(pk=pk)
        db.disconnect()
        return ssp

    def db_import_data_from_db(self, input_db_path: str) -> tuple:
        """Import profiles from another db"""
        in_projects_folder = os.path.dirname(input_db_path)
        in_project_name = os.path.splitext(os.path.basename(input_db_path))[0]
        logger.debug('input: folder: %s, db: %s' % (in_projects_folder, in_project_name))

        in_db = ProjectDb(projects_folder=in_projects_folder, project_name=in_project_name)

        if in_db.get_db_version() > 2:
            raise RuntimeError("unsupported db version: %s" % in_db.get_db_version())
        logger.debug('input project db version: %s' % in_db.get_db_version())

        cur_db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)

        in_lst = in_db.list_profiles()
        cur_lst = cur_db.list_profiles()
        logger.debug('profiles to import: %s' % len(in_lst))
        logger.debug('current profiles: %s' % len(cur_lst))

        # create list of current pks
        cur_pks = list()
        for cur_ssp in cur_lst:
            cur_pks.append("%s;%s" % (cur_ssp[1], cur_ssp[2]))
        # print(cur_pks)

        # copy after having checked that the profile is not already there
        pk_issues = list()
        pk_done = list()

        for in_ssp in in_lst:

            in_key = "%s;%s" % (in_ssp[1], in_ssp[2])
            # print(in_key)
            if in_key in cur_pks:
                pk_issues.append(in_ssp[0])
                continue

            ssp = in_db.profile_by_pk(pk=in_ssp[0])
            success = cur_db.add_casts(ssp)
            if success:
                pk_done.append(in_ssp[0])

            else:
                pk_issues.append(in_ssp[0])

            continue

        in_db.disconnect()

        return pk_issues, pk_done

    def db_timestamp_list(self) -> list:
        """Retrieve a list with the timestamp of all the profiles"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        lst = db.timestamp_list()
        db.disconnect()
        return lst

    def profile_stats(self) -> str:
        msg = str()
        if not self.has_ssp():
            return "Profile not loaded"

        if self.cur.proc.depth[self.cur.proc_valid].size == 0:
            return "Empty profile"

        pre = "<pre style='margin:3px;'>"

        msg += "%s<b>Nr. of Samples</b>: %d</pre>" % (pre, self.cur.proc.depth[self.cur.proc_valid].size)

        msg += "%s           <b>Depth</b>     <b>Sound Speed</b>    <b>Temperature</b>   <b>Salinity</b></pre>" % pre
        msg += "%s<b>min</b>:    % 8.1f %s% 10.1f %s% 8.1f %s% 8.1f %s    </pre>" \
               % (
                   pre,
                   self.cur.proc_depth_min, self.cur.meta.depth_uom,
                   self.cur.proc_speed_min, self.cur.meta.speed_uom,
                   self.cur.proc_temp_min, self.cur.meta.temperature_uom,
                   self.cur.proc_sal_min, self.cur.meta.salinity_uom,
               )
        msg += "%s<b>max</b>:    % 8.1f %s% 10.1f %s% 8.1f %s% 8.1f %s    </pre>" \
               % (
                   pre,
                   self.cur.proc_depth_max, self.cur.meta.depth_uom,
                   self.cur.proc_speed_max, self.cur.meta.speed_uom,
                   self.cur.proc_temp_max, self.cur.meta.temperature_uom,
                   self.cur.proc_sal_max, self.cur.meta.salinity_uom
               )
        # noinspection PyStringFormat
        msg += "%s<b>med</b>:    % 8.1f %s% 10.1f %s% 8.1f %s% 8.1f %s    </pre>" \
               % (
                   pre,
                   self.cur.proc_depth_median, self.cur.meta.depth_uom,
                   self.cur.proc_speed_median, self.cur.meta.speed_uom,
                   self.cur.proc_temp_median, self.cur.meta.temperature_uom,
                   self.cur.proc_sal_median, self.cur.meta.salinity_uom
               )
        msg += "%s<b>avg(*)</b>: % 8.1f %s% 10.1f %s% 8.1f %s% 8.1f %s    </pre>" \
               % (
                   pre,
                   self.cur.proc_depth_mean, self.cur.meta.depth_uom,
                   self.cur.proc_speed_mean, self.cur.meta.speed_uom,
                   self.cur.proc_temp_mean, self.cur.meta.temperature_uom,
                   self.cur.proc_sal_mean, self.cur.meta.salinity_uom
               )
        msg += "%s<b>std</b>:    % 8.1f %s% 10.1f %s% 8.1f %s% 8.1f %s    </pre>" \
               % (
                   pre,
                   self.cur.proc_depth_std, self.cur.meta.depth_uom,
                   self.cur.proc_speed_std, self.cur.meta.speed_uom,
                   self.cur.proc_temp_std, self.cur.meta.temperature_uom,
                   self.cur.proc_sal_std, self.cur.meta.salinity_uom
               )
        msg += "(*) Weighted harmonic mean for sound speed, otherwise arithmetic."

        return msg

    def load_profile(self, pk: int, skip_atlas: Optional[bool] = False) -> bool:
        ssp = self.db_retrieve_profile(pk)
        if not ssp:
            return False

        self.clear_data()
        self.ssp = ssp

        # retrieve atlases data for each retrieved profile
        if self.use_woa09() and self.has_woa09() and not skip_atlas:
            self.ssp.cur.woa09 = self.atlases.woa09.query(lat=self.ssp.cur.meta.latitude,
                                                          lon=self.ssp.cur.meta.longitude,
                                                          dtstamp=self.ssp.cur.meta.utc_time)

        if self.use_woa13() and self.has_woa13() and not skip_atlas:
            self.ssp.cur.woa13 = self.atlases.woa13.query(lat=self.ssp.cur.meta.latitude,
                                                          lon=self.ssp.cur.meta.longitude,
                                                          dtstamp=self.ssp.cur.meta.utc_time)

        if self.use_rtofs() and not skip_atlas:
            try:
                self.ssp.cur.rtofs = self.atlases.rtofs.query(lat=self.ssp.cur.meta.latitude,
                                                              lon=self.ssp.cur.meta.longitude,
                                                              dtstamp=self.ssp.cur.meta.utc_time)
            except RuntimeError:
                self.ssp.cur.rtofs = None
                logger.warning("unable to retrieve RTOFS data")

        if self.use_gomofs() and not skip_atlas:
            try:
                self.ssp.cur.gomofs = self.atlases.gomofs.query(lat=self.ssp.cur.meta.latitude,
                                                                lon=self.ssp.cur.meta.longitude,
                                                                dtstamp=self.ssp.cur.meta.utc_time)
            except RuntimeError:
                self.ssp.cur.gomofs = None
                logger.warning("unable to retrieve GoMOFS data")

        return True

    def delete_db_profile(self, pk: int) -> bool:
        """Retrieve a profile by primary key"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        ret = db.delete_profile_by_pk(pk=pk)
        db.disconnect()
        return ret

    def ray_tracing_comparison(self, pk1: int, pk2: int) -> None:

        avg_depth = 10000.0  # just a very deep value
        half_swath_angle = 70.0  # a safely large angle

        ssp1 = self.db_retrieve_profile(pk1)
        tp1 = TracedProfile(ssp=ssp1.cur, avg_depth=avg_depth,
                            half_swath=half_swath_angle)
        ssp2 = self.db_retrieve_profile(pk2)

        tp2 = TracedProfile(ssp=ssp2.cur, avg_depth=avg_depth,
                            half_swath=half_swath_angle)

        diff = DiffTracedProfiles(old_tp=tp1, new_tp=tp2)
        diff.calc_diff()

        plot = PlotTracedProfiles(diff_tps=diff)
        plot.make_comparison_plots()

    def bias_plots(self, pk1: int, pk2: int) -> None:

        avg_depth = 10000.0  # just a very deep value
        half_swath_angle = 70.0  # a safely large angle

        try:
            ssp1 = self.db_retrieve_profile(pk1)
            tp1 = TracedProfile(ssp=ssp1.cur, avg_depth=avg_depth,
                                half_swath=half_swath_angle)
            ssp2 = self.db_retrieve_profile(pk2)

            tp2 = TracedProfile(ssp=ssp2.cur, avg_depth=avg_depth,
                                half_swath=half_swath_angle)
        except RuntimeError as e:
            traceback.print_stack()
            logger.error(e)
            return

        try:
            diff = DiffTracedProfiles(old_tp=tp1, new_tp=tp2)
            diff.calc_diff()
        except RuntimeError as e:
            traceback.print_stack()
            logger.error(e)
            return

        try:
            plot = PlotTracedProfiles(diff_tps=diff)
            plot.make_bias_plots()

        except RuntimeError as e:
            traceback.print_stack()
            logger.error(e)
            return

    def dqa_at_surface(self, pk: int) -> Optional[str]:
        """Check the sound speed difference between a point measure and the current profile"""

        sn = self.cb.ask_text(title="Enter text", msg="Serial number of surface sound speed instrument")
        if not sn:
            sn = 'Unknown'

        surface_depth = self.cb.ask_number(title="Enter number", msg="Depth of surface sound speed instrument (m)",
                                           default=0, min_value=-10, max_value=30, decimals=1)
        if surface_depth is None:
            logger.error("missing the depth of surface sensor")
            return None

        surface_speed = self.cb.ask_number(title="Enter number", msg="Sound speed measurement of instrument (m/s)",
                                           default=1500, min_value=1300, max_value=1700, decimals=1)
        if surface_speed is None:
            logger.error("missing the sound speed of surface sensor")
            return None

        prof = self.db_retrieve_profile(pk).cur
        cast_speed = prof.interpolate_proc_speed_at_depth(depth=surface_depth)
        speed_diff = abs(cast_speed - surface_speed)

        pre = "<pre style='margin:3px;'>"

        first = "<b>Surface sensor</b> (S/N: %s):" % sn
        second = "%.1f m/sec (at %.2f m)" % (surface_speed, surface_depth)
        msg = "%s%-42s %-36s</pre>" % (pre, first, second)

        first = "<b>Profile</b> (#%02d):" % pk
        second = "%.1f m/sec (interpolated at %.2f m)" % (cast_speed, surface_depth)
        msg += "%s%-42s %-36s</pre>" % (pre, first, second)

        first = "<b>Difference in sound speed</b>:"
        second = "%.2f m/sec" % speed_diff
        msg += "%s%-42s %-36s</pre>" % (pre, first, second)

        if speed_diff > 2.0:
            first = "<b>TEST FAILED</b>:"
            second = "Diff. in sound speed > 2 m/sec"

        else:
            first = "<b>TEST PASSED</b>:"
            second = "Diff. in sound speed <= 2 m/sec"

        msg += "%s%-42s %-36s</pre>" % (pre, first, second)

        return msg

    def dqa_full_profile(self, pk: int, pk_ref: Optional[int] = None, angle: Optional[float] = None) -> Optional[str]:

        if angle is None:
            angle = self.cb.ask_number(title="Enter number", msg="What launch angle(deg) should be checked",
                                       default=60, min_value=0, max_value=90, decimals=0)
            if angle is None:
                logger.error("missing the launch angle to be checked")
                return None

        profile = self.db_retrieve_profile(pk).cur

        if pk_ref is None:
            ref_profile = self.ref.cur
        else:
            ref_profile = self.db_retrieve_profile(pk_ref).cur

        return ref_profile.compare_profile(profile, angle)

    # plotting

    def raise_plot_window(self) -> None:
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        _ = db.plot.raise_window()
        db.disconnect()

    def map_db_profiles(self, pks: Optional[list] = None, show_plot: Optional[bool] = False) -> bool:
        """List the profile on the db"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        ret = db.plot.map_profiles(pks=pks, show_plot=show_plot)
        db.disconnect()
        return ret

    def save_map_db_profiles(self) -> bool:
        """List the profile on the db"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        ret = db.plot.map_profiles(save_fig=True, output_folder=self.outputs_folder)
        db.disconnect()
        return ret

    def aggregate_plot(self, dates: list) -> bool:
        """Create an aggregate plot"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        success = db.plot.aggregate_plot(dates=dates, output_folder=self.outputs_folder, save_fig=False)
        db.disconnect()
        return success

    def save_aggregate_plot(self, dates: list) -> bool:
        """Create an aggregate plot"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        success = db.plot.aggregate_plot(dates=dates, output_folder=self.outputs_folder, save_fig=True)
        db.disconnect()
        return success

    def plot_daily_db_profiles(self) -> bool:
        """Plot the profile on the db by day"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        success = db.plot.daily_plots(project_name=self.current_project,
                                      output_folder=self.outputs_folder, save_fig=False)
        db.disconnect()
        return success

    def save_daily_db_profiles(self) -> bool:
        """Save figure with the profile on the db by day"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        success = db.plot.daily_plots(project_name=self.current_project,
                                      output_folder=self.outputs_folder, save_fig=True)
        db.disconnect()
        return success

    # exporting

    def export_db_profiles_metadata(self, ogr_format: Optional[int] = GdalAux.ogr_formats['ESRI Shapefile'],
                                    filter_fields: Optional['ExportDbFields'] = None) -> bool:
        """Export the db profile metadata"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        success = db.export.export_profiles_metadata(project_name=self.current_project,
                                                     output_folder=self.outputs_folder,
                                                     ogr_format=ogr_format,
                                                     filter_fields=filter_fields)
        db.disconnect()
        return success

    # --- filter

    def filter_cur_data(self) -> bool:
        """Filter/smooth the current profile"""
        if not self.has_ssp():
            logger.warning("no profile!")
            return False

        logger.debug("initial valid samples: %s" % self.cur.nr_valid_proc_samples)

        self.cur.remove_pre_water_entry()
        logger.debug("post-pre-water-removal valid samples: %s" % self.cur.nr_valid_proc_samples)

        self.cur.statistical_filter()
        logger.debug("post-filter valid samples: %s" % self.cur.nr_valid_proc_samples)

        self.cur.cosine_smooth()
        logger.debug("post-smooth valid samples: %s" % self.cur.nr_valid_proc_samples)

        return True

    # --- replace

    def replace_cur_salinity(self) -> bool:
        """Replace salinity using atlases for the current profile"""
        if not self.has_ssp():
            logger.warning("no profile!")
            return False

        if self.setup.ssp_salinity_source == Dicts.atlases['ref']:
            if not self.has_ref():
                logger.warning("missing reference profile")
                return False
            if not self.cur.replace_proc_sal(self.ref):
                return False
            self.cur.modify_proc_info(Dicts.proc_user_infos['REP_SAL_REF'])

        elif self.setup.ssp_salinity_source == Dicts.atlases['RTOFS']:
            if not self.has_rtofs():
                logger.warning("missing RTOFS profile")
                return False
            if not self.cur.replace_proc_sal(self.cur.rtofs):
                return False
            self.cur.modify_proc_info(Dicts.proc_user_infos['REP_SAL_RTOFS'])

        elif self.setup.ssp_salinity_source == Dicts.atlases['GoMOFS']:
            if not self.has_gomofs():
                logger.warning("missing GoMOFS profile")
                return False
            if not self.cur.replace_proc_sal(self.cur.gomofs):
                return False
            self.cur.modify_proc_info(Dicts.proc_user_infos['REP_SAL_GoMOFS'])

        elif self.setup.ssp_salinity_source == Dicts.atlases['WOA09']:
            if not self.has_woa09():
                logger.warning("missing WOA09 profile")
                return False
            if not self.cur.replace_proc_sal(self.cur.woa09):
                return False
            self.cur.modify_proc_info(Dicts.proc_user_infos['REP_SAL_WOA09'])

        elif self.setup.ssp_salinity_source == Dicts.atlases['WOA13']:
            if not self.has_woa13():
                logger.warning("missing WOA13 profile")
                return False
            if not self.cur.replace_proc_sal(self.cur.woa13):
                return False
            self.cur.modify_proc_info(Dicts.proc_user_infos['REP_SAL_WOA13'])

        else:
            logger.warning("unknown atlases: %s" % self.setup.ssp_salinity_source)
            return False

        self.cur.calc_proc_speed()

        return True

    def replace_cur_temp_sal(self) -> bool:
        """Replace temperature/salinity using atlases for the current profile"""
        if not self.has_ssp():
            logger.warning("no profile!")
            return False

        if self.setup.ssp_temp_sal_source == Dicts.atlases['ref']:
            if not self.has_ref():
                logger.warning("missing reference profile")
                return False
            if not self.cur.replace_proc_temp_sal(self.ref):
                return False
            self.cur.modify_proc_info(Dicts.proc_user_infos['REP_TEMP_SAL_REF'])

        elif self.setup.ssp_temp_sal_source == Dicts.atlases['RTOFS']:
            if not self.has_rtofs():
                logger.warning("missing RTOFS profile")
                return False
            if not self.cur.replace_proc_temp_sal(self.cur.rtofs):
                return False
            self.cur.modify_proc_info(Dicts.proc_user_infos['REP_TEMP_SAL_RTOFS'])

        elif self.setup.ssp_temp_sal_source == Dicts.atlases['GoMOFS']:
            if not self.has_gomofs():
                logger.warning("missing GoMOFS profile")
                return False
            if not self.cur.replace_proc_temp_sal(self.cur.gomofs):
                return False
            self.cur.modify_proc_info(Dicts.proc_user_infos['REP_TEMP_SAL_GoMOFS'])

        elif self.setup.ssp_temp_sal_source == Dicts.atlases['WOA09']:
            if not self.has_woa09():
                logger.warning("missing WOA09 profile")
                return False
            if not self.cur.replace_proc_temp_sal(self.cur.woa09):
                return False
            self.cur.modify_proc_info(Dicts.proc_user_infos['REP_TEMP_SAL_WOA09'])

        elif self.setup.ssp_temp_sal_source == Dicts.atlases['WOA13']:
            if not self.has_woa13():
                logger.warning("missing WOA13 profile")
                return False
            if not self.cur.replace_proc_temp_sal(self.cur.woa13):
                return False
            self.cur.modify_proc_info(Dicts.proc_user_infos['REP_TEMP_SAL_WOA13'])

        else:
            logger.warning("unknown atlases: %s" % self.setup.ssp_temp_sal_source)
            return False

        # We don't recalculate speed, of course.  T/S is simply for absorption coefficient calculation

        return True

    def add_cur_tss(self, server_mode: Optional[bool] = False) -> bool:
        """Add the transducer sound speed to the current profile"""
        if not self.has_ssp():
            logger.warning("no profile!")
            return False

        if not self.setup.use_sis4:
            logger.warning("the SIS listening is off")
            return False

        tss_depth = None
        tss_value = None
        if self.listeners.sis4.xyz88:
            try:
                tss_depth = self.listeners.sis4.xyz88.transducer_draft
                tss_value = self.listeners.sis4.xyz88.sound_speed
            except Exception as e:
                logger.warning("unable to retrieve tss values: %s" % e)

        if not tss_depth:
            if not server_mode:
                tss_depth = self.cb.ask_draft()
        if not tss_value:
            if not server_mode:
                tss_value = self.cb.ask_tss()

        if (not tss_depth) or (not tss_value):
            logger.warning("unable to retrieve tss values")
            return False

        self.cur.insert_proc_speed(depth=tss_depth, speed=tss_value, src=Dicts.sources['tss'])
        self.cur.modify_proc_info(Dicts.proc_user_infos['ADD_TSS'])
        return True

    def cur_plotted(self) -> None:
        self.cur.modify_proc_info(Dicts.proc_user_infos['PLOTTED'])

    def extend_profile(self) -> bool:
        if not self.has_ssp():
            logger.warning("no profile!")
            return False

        if self.setup.ssp_extension_source == Dicts.atlases['ref']:
            if not self.has_ref():
                logger.warning("missing reference profile")
                return False
            if not self.cur.extend_profile(self.ref, ext_type=Dicts.sources['ref_ext']):
                return False

        elif self.setup.ssp_extension_source == Dicts.atlases['RTOFS']:
            if not self.has_rtofs():
                logger.warning("missing RTOFS profile")
                return False
            if not self.cur.extend_profile(self.cur.rtofs, ext_type=Dicts.sources['rtofs_ext']):
                return False

        elif self.setup.ssp_extension_source == Dicts.atlases['GoMOFS']:
            if not self.has_gomofs():
                logger.warning("missing GoMOFS profile")
                return False
            if not self.cur.extend_profile(self.cur.gomofs, ext_type=Dicts.sources['gomofs_ext']):
                return False

        elif self.setup.ssp_extension_source == Dicts.atlases['WOA09']:
            if not self.has_woa09():
                logger.warning("missing WOA09 profile")
                return False
            if not self.cur.extend_profile(self.cur.woa09, ext_type=Dicts.sources['woa09_ext']):
                return False

        elif self.setup.ssp_extension_source == Dicts.atlases['WOA13']:
            if not self.has_woa13():
                logger.warning("missing WOA13 profile")
                return False
            if not self.cur.extend_profile(self.cur.woa13, ext_type=Dicts.sources['woa13_ext']):
                return False

        else:
            logger.warning("unknown atlases: %s" % self.setup.ssp_extension_source)
            return False

        return True

    def prepare_sis(self, apply_thin: Optional[bool] = True, apply_12k: Optional[bool] = True,
                    thin_tolerance: Optional[float] = 0.01) -> bool:
        if not self.has_ssp():
            logger.warning("no profile!")
            return False

        self.cur.clone_proc_to_sis()

        if apply_thin:
            if not self.cur.thin(tolerance=thin_tolerance):
                logger.warning("thinning issue")
                return False
        else:
            self.cur.sis.flag[self.cur.sis_valid] = Dicts.flags['thin']

        # filter the data for depth
        si = self.cur.sis_thinned
        valid = self.cur.sis.flag[si][:]
        last_depth = -1.0
        # logger.debug('valid size: %s' % valid.size)
        for i in range(self.cur.sis.flag[si].size):

            depth = self.cur.sis.depth[si][i]
            if abs(depth - last_depth) < 0.02:  # ignore sample with small separation
                valid[i] = Dicts.flags['sis']
                # logger.debug('small change: %s %s %s' % (i, last_depth, depth))

            elif (depth < 0.0) or (depth > 12000.0):
                valid[i] = Dicts.flags['sis']
                # logger.debug('out of range: %s %s' % (i, depth))

            last_depth = depth

        self.cur.sis.flag[si] = valid[:]

        # check depth 0.0
        si = self.cur.sis_thinned
        if self.cur.sis.flag[si].size == 0:
            logger.warning("no valid samples after depth filters")
            return False
        depth_0 = self.cur.sis.depth[si][0]
        if depth_0 > 0:
            self.cur.insert_sis_speed(depth=0.0, speed=self.cur.sis.speed[si][0], src=Dicts.sources['sis'])

        # check last depth
        # Add a final value at 12000m, from: Taira, K., Yanagimoto, D. and Kitagawa, S. (2005).,
        #  "Deep CTD Casts in the Challenger Deep, Mariana Trench", Journal of Oceanography, Vol. 61, pp. 447 t 454
        # TODO: add T/S at location of max depth in the current basin in between last observation and 12000m sample
        if apply_12k:

            si = self.cur.sis_thinned
            if self.cur.sis.flag[si].size == 0:
                logger.warning("no valid samples after depth filters")
                return False
            depth_end = self.cur.sis.depth[si][-1]

            if depth_end < 12000:
                # logger.debug('extending after last depth: %s' % depth_end)
                self.cur.insert_sis_speed(depth=12000.0, speed=1675.8, src=Dicts.sources['sis'],
                                          cond=30.9, temp=2.46, sal=34.70)

            # si = self.cur.sis_thinned
            # logger.debug('last sample: d: %s, temp: %s, sal: %s, speed: %s [%s|%s]'
            #              % (self.cur.sis.depth[si][-1], self.cur.sis.temp[si][-1],
            #                 self.cur.sis.sal[si][-1], self.cur.sis.speed[si][-1],
            #                 self.cur.sis.source[si][-1], self.cur.sis.flag[si][-1]))

        return True

    # --- clear data

    def clear_data(self) -> None:
        """Clear current data"""
        if self.has_ssp():
            logger.debug("Clear SSP data")
            self.ssp = None

    def restart_proc(self) -> None:
        """Clear current data"""
        if self.has_ssp():
            for profile in self.ssp.l:  # we may have multiple profiles
                profile.clone_data_to_proc()
                profile.init_sis()  # initialize to zero
                profile.remove_user_proc_info()  # remove the token that are added by user actions

    # --- plot data

    def plot_ssp(self, more: Optional[bool] = False, show: Optional[bool] = True) -> None:
        """Plot the profiles (mainly for debug)"""
        if self.cur is None:
            return
        from matplotlib import pyplot as plt
        self.ssp.debug_plot(more=more)
        if show:
            plt.show()

    # --- settings

    def settings_db(self) -> ProjectDb:
        return self.setup.db

    def reload_settings_from_db(self) -> None:
        """Reload the current setup from the settings db"""
        self.setup.load_from_db()
        self.check_custom_folders()

    def save_settings_to_db(self) -> None:
        """Save the current setup to settings db"""
        self.setup.save_to_db()

    def clone_setup(self, original_setup_name: str, cloned_setup_name: str) -> None:
        """Clone the passed setup using the passed output name"""

        # first check if the new name is valid
        if self.setup.db.setup_exists(cloned_setup_name):
            logger.warning('setup name duplicated: %s' % cloned_setup_name)
            return

        # create the clone setup
        self.setup.db.add_setup(cloned_setup_name)

        # load the original setup
        original_setup = Setup(release_folder=self.release_folder, use_setup_name=original_setup_name)

        # change the setup in use for input/output
        original_setup.use_setup_name = cloned_setup_name

        # store to db
        original_setup.save_to_db()

    def rename_setup(self, original_setup_name: str, cloned_setup_name: str) -> None:
        """Rename by cloning the passed setup (using the passed output name), then deleting"""
        self.clone_setup(original_setup_name=original_setup_name, cloned_setup_name=cloned_setup_name)
        self.setup.db.delete_setup(original_setup_name)

    # --- atlases
    def use_woa09(self) -> bool:
        return self.setup.use_woa09

    def use_woa13(self) -> bool:
        return self.setup.use_woa13

    def use_rtofs(self) -> bool:
        return self.setup.use_rtofs

    def use_cbofs(self) -> bool:
        return self.setup.use_cbofs

    def use_dbofs(self) -> bool:
        return self.setup.use_dbofs

    def use_gomofs(self) -> bool:
        return self.setup.use_gomofs

    def use_nyofs(self) -> bool:
        return self.setup.use_nyofs

    def use_sjrofs(self) -> bool:
        return self.setup.use_sjrofs

    def use_ngofs(self) -> bool:
        return self.setup.use_ngofs

    def use_tbofs(self) -> bool:
        return self.setup.use_tbofs

    def use_leofs(self) -> bool:
        return self.setup.use_leofs

    def use_lhofs(self) -> bool:
        return self.setup.use_lhofs

    def use_lmofs(self) -> bool:
        return self.setup.use_lmofs

    def use_loofs(self) -> bool:
        return self.setup.use_loofs

    def use_lsofs(self) -> bool:
        return self.setup.use_lsofs

    def use_creofs(self) -> bool:
        return self.setup.use_creofs

    def use_sfbofs(self) -> bool:
        return self.setup.use_sfbofs

    def has_woa09(self) -> bool:
        return self.atlases.woa09.is_present()

    def has_woa13(self) -> bool:
        return self.atlases.woa13.is_present()

    def has_rtofs(self) -> bool:
        return self.atlases.rtofs.is_present()

    def has_cbofs(self) -> bool:
        return self.atlases.cbofs.is_present()

    def has_dbofs(self) -> bool:
        return self.atlases.dbofs.is_present()

    def has_gomofs(self) -> bool:
        return self.atlases.gomofs.is_present()

    def has_nyofs(self) -> bool:
        return self.atlases.nyofs.is_present()

    def has_sjrofs(self) -> bool:
        return self.atlases.sjrofs.is_present()

    def has_ngofs(self) -> bool:
        return self.atlases.ngofs.is_present()

    def has_tbofs(self) -> bool:
        return self.atlases.tbofs.is_present()

    def has_leofs(self) -> bool:
        return self.atlases.leofs.is_present()

    def has_lhofs(self) -> bool:
        return self.atlases.lhofs.is_present()

    def has_lmofs(self) -> bool:
        return self.atlases.lmofs.is_present()

    def has_loofs(self) -> bool:
        return self.atlases.loofs.is_present()

    def has_lsofs(self) -> bool:
        return self.atlases.lsofs.is_present()

    def has_creofs(self) -> bool:
        return self.atlases.creofs.is_present()

    def has_sfbofs(self) -> bool:
        return self.atlases.sfbofs.is_present()

    def download_woa09(self) -> bool:
        return self.atlases.woa09.download_db()

    def download_woa13(self) -> bool:
        return self.atlases.woa13.download_db()

    def download_rtofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.rtofs.download_db(dtstamp=datestamp)

    def download_cbofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.cbofs.download_db(dtstamp=datestamp)

    def download_dbofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.dbofs.download_db(dtstamp=datestamp)

    def download_gomofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.gomofs.download_db(dtstamp=datestamp)

    def download_nyofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.nyofs.download_db(dtstamp=datestamp)

    def download_sjrofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.sjrofs.download_db(dtstamp=datestamp)

    def download_ngofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.ngofs.download_db(dtstamp=datestamp)

    def download_tbofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.tbofs.download_db(dtstamp=datestamp)

    def download_leofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.leofs.download_db(dtstamp=datestamp)

    def download_lhofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.lhofs.download_db(dtstamp=datestamp)

    def download_lmofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.lmofs.download_db(dtstamp=datestamp)

    def download_loofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.loofs.download_db(dtstamp=datestamp)

    def download_lsofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.lsofs.download_db(dtstamp=datestamp)

    def download_creofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.creofs.download_db(dtstamp=datestamp)

    def download_sfbofs(self, datestamp: Optional['datetime'] = None) -> bool:
        return self.atlases.sfbofs.download_db(dtstamp=datestamp)

    # --- listeners

    def use_sis4(self) -> bool:
        return self.setup.use_sis4

    def use_sis5(self) -> bool:
        return self.setup.use_sis5

    def use_sippican(self) -> bool:
        return self.setup.use_sippican

    def use_mvp(self) -> bool:
        return self.setup.use_mvp

    def listen_sis4(self) -> bool:
        return self.listeners.listen_sis4()

    def listen_sis5(self) -> bool:
        return self.listeners.listen_sis5()

    def listen_sippican(self) -> bool:
        return self.listeners.listen_sippican()

    def listen_mvp(self) -> bool:
        return self.listeners.listen_mvp()

    def stop_listen_sis4(self) -> bool:
        return self.listeners.stop_listen_sis4()

    def stop_listen_sis5(self) -> bool:
        return self.listeners.stop_listen_sis5()

    def stop_listen_sippican(self) -> bool:
        return self.listeners.stop_listen_sippican()

    def stop_listen_mvp(self) -> bool:
        return self.listeners.stop_listen_mvp()

    # --- clients

    def transmit_ssp(self) -> bool:
        """Add the transducer sound speed to the current profile"""

        if not self.has_ssp():
            logger.warning("no profile!")
            return False

        if not self.setup.client_list.transmit_ssp(prj=self):
            logger.warning("issue in transmitting the profile")
            return False

        # take care of listeners
        if self.has_sippican_to_process():
            self.listeners.sippican_to_process = False
        if self.has_mvp_to_process():
            self.listeners.mvp_to_process = False
        return True

    # --- server

    def server_is_alive(self) -> bool:
        return self.server.is_alive()

    def start_server(self) -> bool:
        if not self.server.is_alive():
            self.server = Server(prj=self)
            self.server.start()
            time.sleep(0.1)
        return self.server.is_alive()

    def force_server(self) -> bool:
        if not self.server.is_alive():
            raise RuntimeError("Server is not alive")

        self.server.force_send = True
        self.server.check()

        return self.server.is_alive()

    def stop_server(self) -> bool:
        logger.debug("stop server")
        if self.server.is_alive():
            self.server.stop()
            self.server.join(2)
        return not self.server.is_alive()

    # --- logging

    def logging(self) -> None:
        """Set on/off logging for user and server"""
        if self.setup.log_user:
            if not self.logs.user_active:
                self.logs.activate_user_db()
        else:
            if self.logs.user_active:
                self.logs.deactivate_user_db()

        if self.setup.log_server:
            if not self.logs.server_active:
                self.logs.activate_server_db()
        else:
            if self.logs.server_active:
                self.logs.deactivate_server_db()

    # --- repr

    def __repr__(self) -> str:
        msg = "<%s>\n" % self.__class__.__name__
        msg += "\n  <library data folder: %s>\n" % self.data_folder
        msg += "  <projects folder: %s>\n" % self.projects_folder
        msg += "  <release folder: %s>\n" % self.release_folder

        msg += "\n%s" % self.atlases

        msg += "\n  <sqlite_loggers: user %s; server %s>\n" \
               % (self.has_active_user_logger(), self.has_active_server_logger())
        msg += "\n%s" % self.setup

        return msg
