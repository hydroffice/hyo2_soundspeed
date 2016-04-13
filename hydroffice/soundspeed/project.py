from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)

from .base.baseproject import BaseProject
from .base.settings import Settings
from .base.callbacks import Callbacks, AbstractCallbacks
from .base.progress import Progress
from .atlas.atlases import Atlases
from .db.db import SoundSpeedDb
from .base.gdal_aux import GdalAux


class Project(BaseProject):
    """Sound Speed project"""

    def __init__(self, data_folder=None, qprogress=None, qparent=None):
        """Initialization for the library"""
        super(Project, self).__init__(data_folder=data_folder)
        self.setup = Settings(data_folder=self.data_folder)
        self.cb = Callbacks()
        self.ssp = None
        self.atlases = Atlases(prj=self)
        self.progress = Progress(qprogress=qprogress, qparent=qparent)

        self.logging()

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

    # --- callbacks

    def set_callbacks(self, cb):
        """Set user-input callbacks"""
        if not issubclass(type(cb), AbstractCallbacks):
            raise RuntimeError("invalid callbacks object")
        self.cb = cb

    # --- import data

    def import_data(self, data_path, data_format):
        """Import data using a specific format name"""
        idx = self.name_readers.index(data_format)
        reader = self.readers[idx]
        logger.debug("%s > path: %s" % (reader, data_path))
        success = reader.read(data_path=data_path, settings=self.setup, callbacks=self.cb)
        if not success:
            raise RuntimeError("Error using %s reader for file: %s"
                               % (reader.desc, data_path))
        self.ssp = reader.ssp

        # retrieve atlases data
        for pr in self.ssp.l:
            if self.use_woa09() and self.has_woa09():
                pr.woa09 = self.atlases.woa09.query(lat=pr.meta.latitude, lon=pr.meta.longitude,
                                                    datestamp=pr.meta.utc_time)
            if self.use_woa13() and self.has_woa13():
                pr.woa13 = self.atlases.woa13.query(lat=pr.meta.latitude, lon=pr.meta.longitude,
                                                    datestamp=pr.meta.utc_time)
            if self.use_rtofs():
                pr.rtofs = self.atlases.rtofs.query(lat=pr.meta.latitude, lon=pr.meta.longitude,
                                                    datestamp=pr.meta.utc_time)

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

    # --- export data

    def export_data(self, data_formats, data_path, data_files=None):
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
            if not has_data_files:  # we don't have the output file names
                writer.write(ssp=self.ssp, data_path=data_path)
            else:
                writer.write(ssp=self.ssp, data_path=data_path, data_file=data_files[i])

    # --- db

    def store_data(self):
        """Export data using a list of formats name"""

        # checks
        if not self.has_ssp():
            raise RuntimeError("Data not loaded")

        db = SoundSpeedDb(data_folder=self.data_folder)
        ret = db.add_casts(self.ssp)
        db.disconnect()
        return ret

    def db_profiles(self, project=None):
        """List the profile on the db"""
        db = SoundSpeedDb(data_folder=self.data_folder)
        lst = db.list_profiles(project=project)
        db.disconnect()
        return lst

    def db_profile(self, pk):
        """Retrieve a profile by primary key"""
        db = SoundSpeedDb(data_folder=self.data_folder)
        ssp = db.profile_by_pk(pk=pk)
        db.disconnect()
        return ssp

    def delete_db_profile(self, pk):
        """Retrieve a profile by primary key"""
        db = SoundSpeedDb(data_folder=self.data_folder)
        ssp = db.delete_profile_by_pk(pk=pk)
        db.disconnect()
        return ssp

    def map_db_profiles(self, project=None):
        """List the profile on the db"""
        db = SoundSpeedDb(data_folder=self.data_folder)
        lst = db.plot.map_profiles(project=project)
        db.disconnect()
        return lst

    def plot_daily_db_profiles(self, project=None):
        """Plot the profile on the db by day"""
        db = SoundSpeedDb(data_folder=self.data_folder)
        lst = db.plot.daily_plots(project=project)
        db.disconnect()
        return lst

    def save_daily_db_profiles(self, project=None):
        """Save figure with the profile on the db by day"""
        db = SoundSpeedDb(data_folder=self.data_folder)
        lst = db.plot.daily_plots(save_fig=True, project=project)
        db.disconnect()
        return lst

    def export_db_profiles_metadata(self, ogr_format=GdalAux.ogr_formats[b'ESRI Shapefile'],
                                    project=None):
        """Export the db profile metadata"""
        db = SoundSpeedDb(data_folder=self.data_folder)
        lst = db.export.export_profiles_metadata(ogr_format=ogr_format, project=project)
        db.disconnect()
        return lst

    # --- clear data

    def clear_data(self):
        """Clear current data"""
        if self.has_ssp():
            logger.debug("Clear data")
            self.ssp = None

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

    def rtofs_folder(self):
        return self.atlases.rtofs.folder

    def woa09_folder(self):
        return self.atlases.woa09.folder

    def woa13_folder(self):
        return self.atlases.woa13.folder

    def download_rtofs(self, datestamp=None):
        return self.atlases.rtofs.download_db(datestamp=datestamp)

    def download_woa09(self):
        return self.atlases.woa09.download_db()

    def download_woa13(self):
        return self.atlases.woa13.download_db()

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
        msg = "%s" % super(Project, self).__repr__()
        msg += "%s" % self.setup
        return msg
