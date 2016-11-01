from __future__ import absolute_import, division, print_function, unicode_literals

import time
import os
import logging

logger = logging.getLogger(__name__)

from . import __version__ as soundspeed_version
from . import __doc__ as soundspeed_name
from . import formats
from .appdirs.appdirs import user_data_dir
from .atlas.atlases import Atlases
from .base.callbacks import CliCallbacks, AbstractCallbacks
from .base.gdal_aux import GdalAux
from .base.helper import explore_folder
from .base.progress import Progress
from .base.settings import Settings
from .db.db import SoundSpeedDb
from .listener.listeners import Listeners
from .logging.sqlitelogging import SqliteLogging
from .profile.profilelist import ProfileList
from .profile.dicts import Dicts
from .server.server import Server


class SoundSpeedLibrary(object):
    """Sound Speed library"""

    def __init__(self, data_folder=None, qt_progress=None, qt_parent=None):
        """Initialization for the library"""
        logger.info("** > LIB: initializing ...")

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
        self.setup = Settings(data_folder=self.release_folder)
        self.atlases = Atlases(prj=self)
        self.listeners = Listeners(prj=self)
        self.server = Server(prj=self)
        self.logs = SqliteLogging(self._release_folder)  # (user and server) loggers
        self.cb = CliCallbacks()  # default callbacks use command line inputs
        self.progress = Progress(qprogress=qt_progress, qparent=qt_parent)

        self.logging()  # Set on/off logging for user and server based on loaded settings

        logger.info("** > LIB: initialized!")

    def close(self):
        """Destructor"""
        logger.info("CLOSING LIBRARY ...")

        self.listeners.stop()

        if self.server.is_alive():
            self.server.stop()
            self.server.join(2)

        logger.info("LIBRARY CLOSED!")

    # --- library, release, atlases, and projects folders

    def set_folders(self, data_folder):
        """manage library folders creation"""

        # output data folder: where all the library data are written
        self._data_folder = data_folder
        if self._data_folder is None:
            self._data_folder = user_data_dir(soundspeed_name, "HydrOffice")
        if not os.path.exists(self._data_folder):  # create it if it does not exist
            os.makedirs(self._data_folder)
        logger.debug("library folder: %s" % self.data_folder)

        # releases data folder
        self._releases_folder = os.path.join(self.data_folder, "releases")
        if not os.path.exists(self._releases_folder):  # create it if it does not exist
            os.makedirs(self._releases_folder)
        # logger.debug("releases folder: %s" % self.releases_folder)

        # release data folder: release-specific data (as settings)
        self._release_folder = os.path.join(self.releases_folder, soundspeed_version[:soundspeed_version.rindex('.')])
        if not os.path.exists(self._release_folder):  # create it if it does not exist
            os.makedirs(self._release_folder)
        # logger.debug("release folder: %s" % self.release_folder)

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

    @atlases_folder.setter
    def atlases_folder(self, value):
        """ Set the atlases folder"""
        self.atlases.atlases_folder = value

    def open_atlases_folder(self):
        explore_folder(self.atlases_folder)

    @property
    def woa09_folder(self):
        """Get the woa09 atlas folder"""
        return self.atlases.woa09_folder

    @woa09_folder.setter
    def woa09_folder(self, value):
        """ Set the woa09 atlas folder"""
        self.atlases.woa09_folder = value

    @property
    def woa13_folder(self):
        """Get the woa13 atlas folder"""
        return self.atlases.woa13_folder

    @woa13_folder.setter
    def woa13_folder(self, value):
        """ Set the woa13 atlas folder"""
        self.atlases.woa13_folder = value

    @property
    def rtofs_folder(self):
        """Get the rtofs atlas folder"""
        return self.atlases.rtofs_folder

    @rtofs_folder.setter
    def rtofs_folder(self, value):
        """ Set the rtofs atlas folder"""
        self.atlases.rtofs_folder = value

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

    # --- callbacks

    def set_callbacks(self, cb):
        """Set user-input callbacks"""
        if not issubclass(type(cb), AbstractCallbacks):
            raise RuntimeError("invalid callbacks object")
        self.cb = cb

    # --- import data

    def import_data(self, data_path, data_format):
        """Import data using a specific format name"""

        # identify reader to use
        idx = self.name_readers.index(data_format)
        reader = self.readers[idx]
        logger.debug("%s > path: %s" % (data_format, data_path))

        # call the reader to process the data file
        success = reader.read(data_path=data_path, settings=self.setup, callbacks=self.cb)
        if not success:
            raise RuntimeError("Error using %s reader for file: %s"
                               % (reader.desc, data_path))
        self.ssp = reader.ssp
        logger.debug("data file successfully parsed!")

        # retrieve atlases data for each retrieved profile
        for pr in self.ssp.l:

            if self.use_woa09() and self.has_woa09():
                pr.woa09 = self.atlases.woa09.query(lat=pr.meta.latitude, lon=pr.meta.longitude,
                                                    datestamp=pr.meta.utc_time)

            if self.use_woa13() and self.has_woa13():
                pr.woa13 = self.atlases.woa13.query(lat=pr.meta.latitude, lon=pr.meta.longitude,
                                                    datestamp=pr.meta.utc_time)

            if self.use_rtofs():
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

        self.progress.start("Retrieve from SIS")

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

        # create the outputs
        for i, name in enumerate(data_formats):
            idx = self.name_writers.index(name)
            writer = self.writers[idx]
            data_append = False
            if writer.name == 'caris':
                if server_mode:
                    data_append = self.setup.server_append_caris_file
                else:
                    data_append = self.setup.append_caris_file
            if writer.name == 'asvp':
                self.prepare_sis(thin=True)
            if not has_data_files:  # we don't have the output file names
                writer.write(ssp=self.ssp, data_path=data_path, data_append=data_append)
            else:
                writer.write(ssp=self.ssp, data_path=data_path, data_file=data_files[i], data_append=data_append)

        # take care of listeners
        if self.has_sippican_to_process():
            self.listeners.sippican_to_process = False
        if self.has_mvp_to_process():
            self.listeners.mvp_to_process = False

    # --- db

    def store_data(self):
        """Export data using a list of formats name"""

        # checks
        if not self.has_ssp():
            raise RuntimeError("Data not loaded")

        db = SoundSpeedDb(projects_folder=self.projects_folder)
        success = db.add_casts(self.ssp)
        db.disconnect()

        # take care of listeners
        if success:
            if self.has_sippican_to_process():
                self.listeners.sippican_to_process = False
            if self.has_mvp_to_process():
                self.listeners.mvp_to_process = False

        return success

    def db_profiles(self, project=None):
        """List the profile on the db"""
        db = SoundSpeedDb(projects_folder=self.projects_folder)
        lst = db.list_profiles(project=project)
        db.disconnect()
        return lst

    def db_profile(self, pk):
        """Retrieve a profile by primary key"""
        db = SoundSpeedDb(projects_folder=self.projects_folder)
        ssp = db.profile_by_pk(pk=pk)
        db.disconnect()
        return ssp

    def db_timestamp_list(self):
        """Retrieve a list with the timestamp of all the profiles"""
        db = SoundSpeedDb(projects_folder=self.projects_folder)
        lst = db.timestamp_list()
        db.disconnect()
        return lst

    def load_profile(self, pk):
        ssp = self.db_profile(pk)
        if not ssp:
            return False

        self.clear_data()
        self.ssp = ssp
        return True

    def delete_db_profile(self, pk):
        """Retrieve a profile by primary key"""
        db = SoundSpeedDb(projects_folder=self.projects_folder)
        ret = db.delete_profile_by_pk(pk=pk)
        db.disconnect()
        return ret

    def map_db_profiles(self, project=None):
        """List the profile on the db"""
        db = SoundSpeedDb(projects_folder=self.projects_folder)
        ret = db.plot.map_profiles(project=project)
        db.disconnect()
        return ret

    def aggregate_plot(self, dates, project=None):
        """Create an aggregate plot"""
        db = SoundSpeedDb(projects_folder=self.projects_folder)
        success = db.plot.aggregate_plot(dates=dates, project=project)
        db.disconnect()
        return success

    def plot_daily_db_profiles(self, project=None):
        """Plot the profile on the db by day"""
        db = SoundSpeedDb(projects_folder=self.projects_folder)
        success = db.plot.daily_plots(project=project)
        db.disconnect()
        return success

    def save_daily_db_profiles(self, project=None):
        """Save figure with the profile on the db by day"""
        db = SoundSpeedDb(projects_folder=self.projects_folder)
        success = db.plot.daily_plots(save_fig=True, project=project)
        db.disconnect()
        return success

    def export_db_profiles_metadata(self, ogr_format=GdalAux.ogr_formats[b'ESRI Shapefile'],
                                    project=None):
        """Export the db profile metadata"""
        db = SoundSpeedDb(projects_folder=self.projects_folder)
        lst = db.export.export_profiles_metadata(ogr_format=ogr_format, project=project)
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
            self.cur.modify_proc_info('sal.from ref')

        elif self.setup.ssp_salinity_source == Dicts.atlases['RTOFS']:
            if not self.has_rtofs():
                logger.warning("missing RTOFS profile")
                return False
            if not self.cur.replace_proc_sal(self.cur.rtofs):
                return False
            self.cur.modify_proc_info('sal.from RTOFS')

        elif self.setup.ssp_salinity_source == Dicts.atlases['WOA09']:
            if not self.has_woa09():
                logger.warning("missing WOA09 profile")
                return False
            if not self.cur.replace_proc_sal(self.cur.woa09):
                return False
            self.cur.modify_proc_info('sal.from WOA09')

        elif self.setup.ssp_salinity_source == Dicts.atlases['WOA13']:
            if not self.has_woa13():
                logger.warning("missing WOA13 profile")
                return False
            if not self.cur.replace_proc_sal(self.cur.woa13):
                return False
            self.cur.modify_proc_info('sal.from WOA13')

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
            self.cur.modify_proc_info('temp./sal.from ref')

        elif self.setup.ssp_temp_sal_source == Dicts.atlases['RTOFS']:
            if not self.has_rtofs():
                logger.warning("missing RTOFS profile")
                return False
            if not self.cur.replace_proc_temp_sal(self.cur.rtofs):
                return False
            self.cur.modify_proc_info('temp./sal.from RTOFS')

        elif self.setup.ssp_temp_sal_source == Dicts.atlases['WOA09']:
            if not self.has_woa09():
                logger.warning("missing WOA09 profile")
                return False
            if not self.cur.replace_proc_temp_sal(self.cur.woa09):
                return False
            self.cur.modify_proc_info('temp./sal.from WOA09')

        elif self.setup.ssp_temp_sal_source == Dicts.atlases['WOA13']:
            if not self.has_woa13():
                logger.warning("missing WOA13 profile")
                return False
            if not self.cur.replace_proc_temp_sal(self.cur.woa13):
                return False
            self.cur.modify_proc_info('temp./sal.from WOA13')

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
        self.cur.modify_proc_info('added tss')
        return True

    def extend_profile(self):
        if not self.has_ssp():
            logger.warning("no profile!")
            return False

        if self.setup.ssp_extension_source == Dicts.atlases['ref']:
            if not self.has_ref():
                logger.warning("missing reference profile")
                return False
            if not self.cur.extend(self.ref, ext_type=Dicts.sources['ref_ext']):
                return False
            self.cur.modify_proc_info('ext.from ref')

        elif self.setup.ssp_extension_source == Dicts.atlases['RTOFS']:
            if not self.has_rtofs():
                logger.warning("missing RTOFS profile")
                return False
            if not self.cur.extend(self.cur.rtofs, ext_type=Dicts.sources['rtofs_ext']):
                return False
            self.cur.modify_proc_info('ext.from RTOFS')

        elif self.setup.ssp_extension_source == Dicts.atlases['WOA09']:
            if not self.has_woa09():
                logger.warning("missing WOA09 profile")
                return False
            if not self.cur.extend(self.cur.woa09, ext_type=Dicts.sources['woa09_ext']):
                return False
            self.cur.modify_proc_info('ext.from WOA09')

        elif self.setup.ssp_extension_source == Dicts.atlases['WOA13']:
            if not self.has_woa13():
                logger.warning("missing WOA13 profile")
                return False
            if not self.cur.extend(self.cur.woa13, ext_type=Dicts.sources['woa13_ext']):
                return False
            self.cur.modify_proc_info('ext.from WOA13')

        else:
            logger.warning("unknown atlases: %s" % self.setup.ssp_extension_source)
            return False

        return True

    def prepare_sis(self, thin=True):
        if not self.has_ssp():
            logger.warning("no profile!")
            return False

        self.cur.clone_proc_to_sis()

        if not thin:
            return True

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
        self.setup.load_settings_from_db()

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

    def start_server(self):
        if not self.server.is_alive():
            self.server = Server(prj=self)
            self.server.start()
            time.sleep(0.1)
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
