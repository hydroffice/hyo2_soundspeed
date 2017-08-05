import numpy as np
import time
import os
import copy
import shutil
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed import __version__ as soundspeed_version
from hyo.soundspeed import __doc__ as soundspeed_name
from hyo.soundspeed import formats
from hyo.soundspeed.appdirs.appdirs import user_data_dir
from hyo.soundspeed.atlas.atlases import Atlases
from hyo.soundspeed.base.callbacks.abstract_callbacks import AbstractCallbacks
from hyo.soundspeed.base.callbacks.cli_callbacks import CliCallbacks
from hyo.soundspeed.base.gdal_aux import GdalAux
from hyo.soundspeed.base.helper import explore_folder
from hyo.soundspeed.base.progress.abstract_progress import AbstractProgress
from hyo.soundspeed.base.progress.cli_progress import CliProgress
from hyo.soundspeed.base.setup import Setup
from hyo.soundspeed.db.db import ProjectDb
from hyo.soundspeed.listener.listeners import Listeners
from hyo.soundspeed.logging.sqlitelogging import SqliteLogging
from hyo.soundspeed.profile.profilelist import ProfileList
from hyo.soundspeed.profile.dicts import Dicts
from hyo.soundspeed.server.server import Server
# from hyo.soundspeed.monitor.monitor import SurveyDataMonitor


class SoundSpeedLibrary(object):
    """Sound Speed library"""

    def __init__(self, data_folder=None, callbacks=CliCallbacks(), progress=CliProgress()):
        """Initialization for the library"""
        logger.info("** > LIB: initializing ...")

        # callbacks
        if not issubclass(type(callbacks), AbstractCallbacks):
            raise RuntimeError("invalid callbacks object")
        self.cb = callbacks
        # progress bar
        if not issubclass(type(progress), AbstractProgress):
            raise RuntimeError("invalid progress object")
        self.progress = progress

        self.ssp = None  # current profile
        self.ref = None  # reference profile

        # take care of all the required folders
        self._data_folder = None
        self._releases_folder = None
        self._release_folder = None
        self._projects_folder = None
        self._outputs_folder = None
        self.set_folders(data_folder=data_folder)

        # load settings and other functionalities
        self.setup = Setup(release_folder=self.release_folder)
        self.atlases = Atlases(prj=self)
        self.check_custom_folders()
        self.listeners = Listeners(prj=self)
        self.cb.sis_listener = self.listeners.sis  # to provide default values from SIS (if available)
        self.server = Server(prj=self)
        self.logs = SqliteLogging(self._release_folder)  # (user and server) loggers

        self.logging()  # Set on/off logging for user and server based on loaded settings

        logger.info("** > LIB: initialized!")

    def check_custom_folders(self):
        logger.info("Checking for custom folders")

        # projects folder
        if len(self.setup.custom_projects_folder):

            if os.path.exists(self.setup.custom_projects_folder):
                self.projects_folder = self.setup.custom_projects_folder
            else:  # delete the not-existing folder
                self.setup.custom_projects_folder = str()
                self.setup.save_to_db()

        # outputs folder
        if len(self.setup.custom_outputs_folder):

            if os.path.exists(self.setup.custom_outputs_folder):
                self.outputs_folder = self.setup.custom_outputs_folder
            else:  # delete the not-existing folder
                self.setup.custom_outputs_folder = str()
                self.setup.save_to_db()

    def close(self):
        """Destructor"""
        logger.info("** > LIB: closing ...")

        self.listeners.stop()

        if self.server.is_alive():
            self.server.stop()
            self.server.join(2)

        logger.info("** > LIB: closed!")

    # --- library, release, atlases, and projects folders

    @classmethod
    def make_data_folder(cls, data_folder=None):

        # output data folder: where all the library data are written
        if data_folder is None:
            data_folder = user_data_dir(soundspeed_name, "HydrOffice")
        if not os.path.exists(data_folder):  # create it if it does not exist
            os.makedirs(data_folder)
        # logger.debug("library folder: %s" % data_folder)
        return data_folder

    @classmethod
    def make_releases_folder(cls, data_folder=None):

        data_folder = cls.make_data_folder(data_folder=data_folder)

        # releases data folder
        releases_folder = os.path.join(data_folder, "releases")
        if not os.path.exists(releases_folder):  # create it if it does not exist
            os.makedirs(releases_folder)
        # logger.debug("releases folder: %s" % self.releases_folder)

        return releases_folder

    @classmethod
    def make_release_folder(cls, data_folder=None):
        # release data folder: release-specific data (as settings)
        releases_folder = cls.make_releases_folder(data_folder=data_folder)
        release_folder = os.path.join(releases_folder, soundspeed_version[:soundspeed_version.rindex('.')])
        if not os.path.exists(release_folder):  # create it if it does not exist
            os.makedirs(release_folder)
        # logger.debug("release folder: %s" % self.release_folder)

        return release_folder

    @classmethod
    def setup_exists(cls, data_folder=None):
        release_folder = cls.make_release_folder()
        return os.path.exists(os.path.join(release_folder, "setup.db"))

    @classmethod
    def list_other_setups(cls, data_folder=None):
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
            except Exception:
                continue

            logger.debug("found setup: %s" % setup_path)
            old_setups.append(setup_path)

        return old_setups

    @classmethod
    def copy_setup(cls, input_setup, data_folder=None):
        from shutil import copyfile
        release_folder = cls.make_release_folder()
        output_setup = os.path.join(release_folder, "setup.db")
        copyfile(input_setup, output_setup)
        logger.info("copied from: %s to: %s" % (input_setup, output_setup))

    def set_folders(self, data_folder):
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
    def data_folder(self):
        """Get the library data folder"""
        return self._data_folder

    @data_folder.setter
    def data_folder(self, value):
        """ Set the library data folder"""
        self._data_folder = value

    def open_data_folder(self):
        explore_folder(self.data_folder)

    # releases folder

    @property
    def releases_folder(self):
        """Get the releases data folder"""
        return self._releases_folder

    @releases_folder.setter
    def releases_folder(self, value):
        """ Set the releases data folder"""
        self._releases_folder = value

    def open_releases_folder(self):
        explore_folder(self.releases_folder)

    # release folder

    @property
    def release_folder(self):
        """Get the release data folder"""
        return self._release_folder

    @release_folder.setter
    def release_folder(self, value):
        """ Set the release data folder"""
        self._release_folder = value

    # atlases

    @property
    def atlases_folder(self):
        """Get the atlases folder"""
        return self.atlases.atlases_folder

    def open_atlases_folder(self):
        explore_folder(self.atlases_folder)

    @property
    def woa09_folder(self):
        """Get the woa09 atlas folder"""
        return self.atlases.woa09_folder

    @property
    def woa13_folder(self):
        """Get the woa13 atlas folder"""
        return self.atlases.woa13_folder

    @property
    def rtofs_folder(self):
        """Get the rtofs atlas folder"""
        return self.atlases.rtofs_folder

    # projects

    @property
    def projects_folder(self):
        """Get the projects folder"""
        return self._projects_folder

    @projects_folder.setter
    def projects_folder(self, value):
        """ Set the projects folder"""
        self._projects_folder = value

    def open_projects_folder(self):
        explore_folder(self.projects_folder)

    # outputs

    @property
    def outputs_folder(self):
        """Get the outputs folder"""
        return self._outputs_folder

    @outputs_folder.setter
    def outputs_folder(self, value):
        """ Set the outputs folder"""
        self._outputs_folder = value

    def open_outputs_folder(self):
        explore_folder(self.outputs_folder)

    # --- readers/writers

    @property
    def readers(self):
        return formats.readers

    @property
    def name_readers(self):
        return formats.name_readers

    @property
    def ext_readers(self):
        return formats.ext_readers

    @property
    def desc_readers(self):
        return formats.desc_readers

    @property
    def writers(self):
        return formats.writers

    @property
    def name_writers(self):
        return formats.name_writers

    @property
    def ext_writers(self):
        return formats.ext_writers

    @property
    def desc_writers(self):
        return formats.desc_writers

    # --- sqlite logging

    def has_active_user_logger(self):
        return self.logs.user_active

    def activate_user_logger(self, flag):
        if flag:
            self.logs.activate_user_db()
        else:
            self.logs.deactivate_user_db()

    def has_active_server_logger(self):
        return self.logs.server_active

    def activate_server_logger(self, flag):
        if flag:
            self.logs.activate_server_db()
        else:
            self.logs.deactivate_server_db()

    # --- ssp profile

    @property
    def ssp_list(self):
        return self.ssp

    @property
    def cur(self):
        if self.ssp is None:
            return None
        return self.ssp.cur

    @property
    def cur_basename(self):
        if self.cur is None:
            return "output"
        if self.cur.meta.original_path is None:
            return "output"
        return os.path.basename(self.cur.meta.original_path).split('.')[0]

    @property
    def cur_file(self):
        if self.cur is None:
            return None
        if self.cur.meta.original_path is None:
            return None
        return os.path.basename(self.cur.meta.original_path)

    def has_ssp(self):
        if self.cur is None:
            return False
        return True

    def has_ref(self):
        if self.ref is None:
            return False
        return True

    # --- listeners

    def has_mvp_to_process(self):
        if not self.use_mvp():
            return False

        return self.listeners.mvp_to_process

    def has_sippican_to_process(self):
        if not self.use_sippican():
            return False

        return self.listeners.sippican_to_process

    # --- import data

    def import_data(self, data_path, data_format, skip_atlas=False):
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

        # retrieve atlases data for each retrieved profile
        for pr in self.ssp.l:

            if self.use_woa09() and self.has_woa09() and not skip_atlas:
                pr.woa09 = self.atlases.woa09.query(lat=pr.meta.latitude, lon=pr.meta.longitude,
                                                    datestamp=pr.meta.utc_time)

            if self.use_woa13() and self.has_woa13() and not skip_atlas:
                pr.woa13 = self.atlases.woa13.query(lat=pr.meta.latitude, lon=pr.meta.longitude,
                                                    datestamp=pr.meta.utc_time)

            if self.use_rtofs() and not skip_atlas:
                try:
                    pr.rtofs = self.atlases.rtofs.query(lat=pr.meta.latitude, lon=pr.meta.longitude,
                                                        datestamp=pr.meta.utc_time)
                except RuntimeError:
                    pr.rtofs = None
                    logger.warning("unable to retrieve RTOFS data")

    # --- receive data

    def retrieve_woa09(self):
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

        self.ssp = self.atlases.woa09.query(lat=lat, lon=lon, datestamp=utc_time)

    def retrieve_woa13(self):
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

        self.ssp = self.atlases.woa13.query(lat=lat, lon=lon, datestamp=utc_time)

    def retrieve_rtofs(self):
        """Retrieve data from RTOFS atlas"""

        utc_time = self.cb.ask_date()
        if utc_time is None:
            logger.error("missing date required for database lookup")
            return None

        if not self.download_rtofs(datestamp=utc_time):
            logger.error("unable to download RTOFS atlas data set")
            return None

        if not self.has_rtofs():
            logger.error("missing RTOFS atlas data set")
            return None

        lat, lon = self.cb.ask_location()
        if (lat is None) or (lon is None):
            logger.error("missing geographic location required for database lookup")
            return None

        self.ssp = self.atlases.rtofs.query(lat=lat, lon=lon, datestamp=utc_time)

    def retrieve_sis(self):
        """Retrieve data from SIS"""
        if not self.use_sis():
            logger.warning("use SIS option is disabled")
            return

        self.progress.start(text="Retrieve from SIS")

        self.listen_sis()

        prog_quantum = 50 / len(self.setup.client_list.clients)

        for client in self.setup.client_list.clients:
            client.request_profile_from_sis(prj=self)
            self.progress.add(prog_quantum)

        if not self.listeners.sis.ssp:
            self.progress.end()
            raise RuntimeError("Unable to get SIS cast from any clients")

        # logger.info("got SSP from SIS: %s" % self.listeners.sis.ssp)
        self.progress.update(80)

        # try to retrieve the location from SIS
        lat = None
        lon = None
        if self.listeners.sis.nav:
            from_sis = self.cb.ask_location_from_sis()
            if from_sis:
                lat, lon = self.listeners.sis.nav.latitude, self.listeners.sis.nav.longitude
        # if we don't have a location, ask user
        if (lat is None) or (lon is None):
            lat, lon = self.cb.ask_location()
            if (lat is None) or (lon is None):
                logger.error("missing geographic location required for database lookup")
                self.progress.end()
                return None

        ssp = self.listeners.sis.ssp.convert_ssp()
        ssp.meta.latitude = lat
        ssp.meta.longitude = lon
        ssp.clone_data_to_proc()
        ssp.init_sis()  # initialize to zero
        ssp_list = ProfileList()
        ssp_list.append_profile(ssp)
        self.ssp = ssp_list
        self.progress.end()

    # --- export data

    def export_data(self, data_formats, data_path, data_files=None, server_mode=False):
        """Export data using a list of formats name"""

        # checks
        if not self.has_ssp():
            raise RuntimeError("Data not loaded")
        if type(data_formats) is not list:
            raise RuntimeError("Passed %s in place of list" % type(data_formats))

        has_data_files = False
        if data_files is not None:
            if len(data_files) == 0:
                has_data_files = False
            elif len(data_formats) != len(data_files):
                raise RuntimeError("Mismatch between format and file lists")
            else:
                has_data_files = True

        if data_path is None:
            data_path = self.outputs_folder

        # create the outputs
        for i, name in enumerate(data_formats):

            # special case: synthetic multiple profiles, we just save the average profile
            if (name == 'ncei') and (self.ssp.l[0].meta.sensor_type == Dicts.sensor_types['Synthetic']):
                raise RuntimeError("Attempt to export a synthetic profile in NCEI format!")

            idx = self.name_writers.index(name)
            writer = self.writers[idx]

            # special case for Kongsberg asvp format
            if writer.name == 'asvp':
                self.prepare_sis()

            # special case for Fugro ISS format with NCEI format
            if (name == 'ncei') and (self.ssp.l[0].meta.probe_type == Dicts.probe_types['ISS']):
                logger.info("special case: NCEI and ISS format")
                instrument = self.cb.ask_text("ISS for NCEI", "Enter the instrument type and model \n"
                                                              "(if you don't know, leave it blank):")
                # if empty, we just use the sensor type
                if instrument is None or instrument == "":
                    instrument = self.ssp.l[0].meta.sensor
                writer.instrument = instrument

            if not has_data_files:  # we don't have the output file names
                if len(data_formats) == 1 and name == 'ncei':  # NCEI requires special filename convention
                    writer.write(ssp=self.ssp, data_path=data_path, data_file='ncei', project=self.current_project)
                else:
                    writer.write(ssp=self.ssp, data_path=data_path, project=self.current_project)
            else:
                writer.write(ssp=self.ssp, data_path=data_path, data_file=data_files[i], project=self.current_project)

        # take care of listeners
        if self.has_sippican_to_process():
            self.listeners.sippican_to_process = False
        if self.has_mvp_to_process():
            self.listeners.mvp_to_process = False

    # --- project db

    @property
    def current_project(self):
        return self.setup.current_project

    @current_project.setter
    def current_project(self, value):
        self.setup.current_project = value

    def rename_current_project(self, name):
        old_db_path = os.path.join(self.projects_folder, self.current_project + ".db")
        if not os.path.exists(old_db_path):
            raise RuntimeError("unable to locate the current project: %s" % old_db_path)

        new_db_path = os.path.join(self.projects_folder, name + ".db")
        if os.path.exists(new_db_path):
            raise RuntimeError("the project already exists: %s" % new_db_path)

        shutil.copy(old_db_path, new_db_path)
        if not os.path.exists(new_db_path):
            raise RuntimeError("unable to copy the project db: %s" % new_db_path)

        os.remove(old_db_path)

        self.current_project = name
        self.save_settings_to_db()
        self.reload_settings_from_db()

    def remove_project(self, name):
        if name == self.current_project:
            raise RuntimeError("unable to remove the current project: %s" % self.current_project)

        db_path = os.path.join(self.projects_folder, name + ".db")
        if not os.path.exists(db_path):
            raise RuntimeError("unable to locate the project to delete: %s" % db_path)

        os.remove(db_path)

    def list_projects(self):
        """Return a list with all the available projects"""
        prj_list = list()
        for root, dirs, files in os.walk(self.projects_folder):
            for f in files:
                if f.endswith('.db'):
                    prj_list.append(os.path.splitext(os.path.basename(f))[0])
        return prj_list

    def remove_data(self):
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

    def store_data(self):
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

    def db_list_profiles(self, project=None):
        """List the profile on the db"""
        if project is None:
            project = self.current_project

        db = ProjectDb(projects_folder=self.projects_folder, project_name=project)
        lst = db.list_profiles()
        db.disconnect()
        return lst

    def db_retrieve_profile(self, pk):
        """Retrieve a profile by primary key"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        ssp = db.profile_by_pk(pk=pk)
        db.disconnect()
        return ssp

    def db_import_data_from_db(self, input_db_path):
        """Import profiles from another db"""
        in_projects_folder = os.path.dirname(input_db_path)
        in_project_name = os.path.splitext(os.path.basename(input_db_path))[0]
        logger.debug('input: folder: %s, db: %s' % (in_projects_folder, in_project_name))

        in_db = ProjectDb(projects_folder=in_projects_folder, project_name=in_project_name)

        if in_db.get_db_version() > 1:
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

    def db_timestamp_list(self):
        """Retrieve a list with the timestamp of all the profiles"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        lst = db.timestamp_list()
        db.disconnect()
        return lst

    def profile_stats(self):
        msg = str()
        if not self.has_ssp():
            return "Profile not loaded"

        if self.cur.proc.depth[self.cur.proc_valid].size == 0:
            return "Empty profile"

        pre = "<pre style='margin:3px;'>"

        msg += "%s<b>Nr. of Samples</b>: %d</pre>" % (pre, self.cur.proc.depth[self.cur.proc_valid].size)

        msg += "%s        <b>Depth</b>     <b>Sound Speed</b>    <b>Temperature</b>   <b>Salinity</b></pre>" % pre
        msg += "%s<b>min</b>: % 8.1f %s% 10.1f %s% 8.1f %s% 8.1f %s    </pre>" \
               % (
                   pre,
                   self.cur.proc.depth[self.cur.proc_valid].min(), self.cur.meta.depth_uom,
                   self.cur.proc.speed[self.cur.proc_valid].min(), self.cur.meta.speed_uom,
                   self.cur.proc.temp[self.cur.proc_valid].min(), self.cur.meta.temperature_uom,
                   self.cur.proc.sal[self.cur.proc_valid].min(), self.cur.meta.salinity_uom,
               )
        msg += "%s<b>max</b>: % 8.1f %s% 10.1f %s% 8.1f %s% 8.1f %s    </pre>" \
               % (
                   pre,
                   self.cur.proc.depth[self.cur.proc_valid].max(), self.cur.meta.depth_uom,
                   self.cur.proc.speed[self.cur.proc_valid].max(), self.cur.meta.speed_uom,
                   self.cur.proc.temp[self.cur.proc_valid].max(), self.cur.meta.temperature_uom,
                   self.cur.proc.sal[self.cur.proc_valid].max(), self.cur.meta.salinity_uom
               )
        # noinspection PyStringFormat
        msg += "%s<b>med</b>: % 8.1f %s% 10.1f %s% 8.1f %s% 8.1f %s    </pre>" \
               % (
                   pre,
                   np.median(self.cur.proc.depth[self.cur.proc_valid]), self.cur.meta.depth_uom,
                   np.median(self.cur.proc.speed[self.cur.proc_valid]), self.cur.meta.speed_uom,
                   np.median(self.cur.proc.temp[self.cur.proc_valid]), self.cur.meta.temperature_uom,
                   np.median(self.cur.proc.sal[self.cur.proc_valid]), self.cur.meta.salinity_uom
               )
        msg += "%s<b>avg</b>: % 8.1f %s% 10.1f %s% 8.1f %s% 8.1f %s    </pre>" \
               % (
                   pre,
                   np.average(self.cur.proc.depth[self.cur.proc_valid]), self.cur.meta.depth_uom,
                   np.average(self.cur.proc.speed[self.cur.proc_valid]), self.cur.meta.speed_uom,
                   np.average(self.cur.proc.temp[self.cur.proc_valid]), self.cur.meta.temperature_uom,
                   np.average(self.cur.proc.sal[self.cur.proc_valid]), self.cur.meta.salinity_uom
               )
        msg += "%s<b>std</b>: % 8.1f %s% 10.1f %s% 8.1f %s% 8.1f %s    </pre>" \
               % (
                   pre,
                   self.cur.proc.depth[self.cur.proc_valid].std(), self.cur.meta.depth_uom,
                   self.cur.proc.speed[self.cur.proc_valid].std(), self.cur.meta.speed_uom,
                   self.cur.proc.temp[self.cur.proc_valid].std(), self.cur.meta.temperature_uom,
                   self.cur.proc.sal[self.cur.proc_valid].std(), self.cur.meta.salinity_uom
               )

        return msg

    def load_profile(self, pk, skip_atlas=False):
        ssp = self.db_retrieve_profile(pk)
        if not ssp:
            return False

        self.clear_data()
        self.ssp = ssp

        # retrieve atlases data for each retrieved profile
        if self.use_woa09() and self.has_woa09() and not skip_atlas:
            self.ssp.cur.woa09 = self.atlases.woa09.query(lat=self.ssp.cur.meta.latitude,
                                                          lon=self.ssp.cur.meta.longitude,
                                                          datestamp=self.ssp.cur.meta.utc_time)

        if self.use_woa13() and self.has_woa13() and not skip_atlas:
            self.ssp.cur.woa13 = self.atlases.woa13.query(lat=self.ssp.cur.meta.latitude,
                                                          lon=self.ssp.cur.meta.longitude,
                                                          datestamp=self.ssp.cur.meta.utc_time)

        if self.use_rtofs() and not skip_atlas:
            try:
                self.ssp.cur.rtofs = self.atlases.rtofs.query(lat=self.ssp.cur.meta.latitude,
                                                              lon=self.ssp.cur.meta.longitude,
                                                              datestamp=self.ssp.cur.meta.utc_time)
            except RuntimeError:
                self.ssp.cur.rtofs = None
                logger.warning("unable to retrieve RTOFS data")

        return True

    def delete_db_profile(self, pk):
        """Retrieve a profile by primary key"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        ret = db.delete_profile_by_pk(pk=pk)
        db.disconnect()
        return ret

    def dqa_at_surface(self, pk):
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

    def dqa_full_profile(self, pk, pk_ref=None, angle=None):

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

    def raise_plot_window(self):
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        _ = db.plot.raise_window()
        db.disconnect()

    def map_db_profiles(self):
        """List the profile on the db"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        ret = db.plot.map_profiles(output_folder=self.outputs_folder, save_fig=False)
        db.disconnect()
        return ret

    def save_map_db_profiles(self):
        """List the profile on the db"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        ret = db.plot.map_profiles(output_folder=self.outputs_folder, save_fig=True)
        db.disconnect()
        return ret

    def aggregate_plot(self, dates):
        """Create an aggregate plot"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        success = db.plot.aggregate_plot(dates=dates, output_folder=self.outputs_folder, save_fig=False)
        db.disconnect()
        return success

    def save_aggregate_plot(self, dates):
        """Create an aggregate plot"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        success = db.plot.aggregate_plot(dates=dates, output_folder=self.outputs_folder, save_fig=True)
        db.disconnect()
        return success

    def plot_daily_db_profiles(self):
        """Plot the profile on the db by day"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        success = db.plot.daily_plots(project_name=self.current_project,
                                      output_folder=self.outputs_folder, save_fig=False)
        db.disconnect()
        return success

    def save_daily_db_profiles(self):
        """Save figure with the profile on the db by day"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        success = db.plot.daily_plots(project_name=self.current_project,
                                      output_folder=self.outputs_folder, save_fig=True)
        db.disconnect()
        return success

    # exporting

    def export_db_profiles_metadata(self, ogr_format=GdalAux.ogr_formats['ESRI Shapefile']):
        """Export the db profile metadata"""
        db = ProjectDb(projects_folder=self.projects_folder, project_name=self.current_project)
        lst = db.export.export_profiles_metadata(project_name=self.current_project,
                                                 output_folder=self.outputs_folder,
                                                 ogr_format=ogr_format)
        db.disconnect()
        return lst

    # --- replace

    def replace_cur_salinity(self):
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

    def replace_cur_temp_sal(self):
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

    def add_cur_tss(self, server_mode=False):
        """Add the transducer sound speed to the current profile"""
        if not self.has_ssp():
            logger.warning("no profile!")
            return False

        if not self.setup.use_sis:
            logger.warning("the SIS listening is off")
            return False

        tss_depth = None
        tss_value = None
        if self.listeners.sis.xyz88:
            try:
                tss_depth = self.listeners.sis.xyz88.transducer_draft
                tss_value = self.listeners.sis.xyz88.sound_speed
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

    def cur_plotted(self):
        self.cur.modify_proc_info(Dicts.proc_user_infos['PLOTTED'])

    def extend_profile(self):
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

    def prepare_sis(self):
        if not self.has_ssp():
            logger.warning("no profile!")
            return False

        self.cur.clone_proc_to_sis()

        if not self.cur.thin(tolerance=0.1):
            logger.warning("thinning issue")
            return False

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
        si = self.cur.sis_thinned
        if self.cur.sis.flag[si].size == 0:
            logger.warning("no valid samples after depth filters")
            return False
        depth_end = self.cur.sis.depth[si][-1]
        if depth_end < 12000:
            self.cur.insert_sis_speed(depth=12000.0, speed=1675.8, src=Dicts.sources['sis'])
            si = self.cur.sis_thinned
            self.cur.sis.temp[si][-1] = 2.46
            self.cur.sis.sal[si][-1] = 34.70
        # logger.debug('last sample: %s %s %s %s'
        #              % (self.cur.sis.depth[-1], self.cur.sis.speed[-1],
        #                 self.cur.sis.source[-1], self.cur.sis.flag[-1]))

        return True

    # --- clear data

    def clear_data(self):
        """Clear current data"""
        if self.has_ssp():
            logger.debug("Clear SSP data")
            self.ssp = None

    def restart_proc(self):
        """Clear current data"""
        if self.has_ssp():
            for profile in self.ssp.l:  # we may have multiple profiles
                profile.clone_data_to_proc()
                profile.init_sis()  # initialize to zero
                profile.remove_user_proc_info()  # remove the token that are added by user actions

    # --- plot data

    def plot_ssp(self, more=False, show=True):
        """Plot the profiles (mainly for debug)"""
        if self.cur is None:
            return
        from matplotlib import pyplot as plt
        self.ssp.debug_plot(more=more)
        if show:
            plt.show()

    # --- settings

    def settings_db(self):
        return self.setup.db

    def reload_settings_from_db(self):
        """Reload the current setup from the settings db"""
        self.setup.load_from_db()
        self.check_custom_folders()

    def save_settings_to_db(self):
        """Save the current setup to settings db"""
        self.setup.save_to_db()

    def clone_setup(self, original_setup_name, cloned_setup_name):
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

    def rename_setup(self, original_setup_name, cloned_setup_name):
        """Rename by cloning the passed setup (using the passed output name), then deleting"""
        self.clone_setup(original_setup_name=original_setup_name, cloned_setup_name=cloned_setup_name)
        self.setup.db.delete_setup(original_setup_name)

    # --- atlases

    def use_rtofs(self):
        return self.setup.use_rtofs

    def use_woa09(self):
        return self.setup.use_woa09

    def use_woa13(self):
        return self.setup.use_woa13

    def has_rtofs(self):
        return self.atlases.rtofs.is_present()

    def has_woa09(self):
        return self.atlases.woa09.is_present()

    def has_woa13(self):
        return self.atlases.woa13.is_present()

    def download_rtofs(self, datestamp=None):
        return self.atlases.rtofs.download_db(datestamp=datestamp)

    def download_woa09(self):
        return self.atlases.woa09.download_db()

    def download_woa13(self):
        return self.atlases.woa13.download_db()

    # --- listeners

    def use_sis(self):
        return self.setup.use_sis

    def use_sippican(self):
        return self.setup.use_sippican

    def use_mvp(self):
        return self.setup.use_mvp

    def listen_sis(self):
        return self.listeners.listen_sis()

    def listen_sippican(self):
        return self.listeners.listen_sippican()

    def listen_mvp(self):
        return self.listeners.listen_mvp()

    def stop_listen_sis(self):
        return self.listeners.stop_listen_sis()

    def stop_listen_sippican(self):
        return self.listeners.stop_listen_sippican()

    def stop_listen_mvp(self):
        return self.listeners.stop_listen_mvp()

    # --- clients

    def transmit_ssp(self):
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

    def server_is_alive(self):
        return self.server.is_alive()

    def start_server(self):
        if not self.server.is_alive():
            self.server = Server(prj=self)
            self.server.start()
            time.sleep(0.1)
        return self.server.is_alive()

    def force_server(self):
        if not self.server.is_alive():
            raise RuntimeError("Server is not alive")

        self.server.force_send.set()
        self.server.check()

        return self.server.is_alive()

    def stop_server(self):
        logger.debug("stop server")
        if self.server.is_alive():
            self.server.stop()
            self.server.join(2)
        return not self.server.is_alive()

    # --- logging

    def logging(self):
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

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__
        msg += "\n  <library data folder: %s>\n" % self.data_folder
        msg += "  <projects folder: %s>\n" % self.projects_folder
        msg += "  <release folder: %s>\n" % self.release_folder

        msg += "\n%s" % self.atlases

        msg += "\n  <sqlite_loggers: user %s; server %s>\n" \
               % (self.has_active_user_logger(), self.has_active_server_logger())
        msg += "\n%s" % self.setup
        return msg
