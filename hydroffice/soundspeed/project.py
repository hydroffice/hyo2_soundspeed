from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)

from .base.baseproject import BaseProject
from .base.settings import Settings
from .base.callbacks import Callbacks, AbstractCallbacks


class Project(BaseProject):
    """Sound Speed project"""

    def __init__(self, data_folder=None):
        """Initialization for the library"""
        super(Project, self).__init__(data_folder=data_folder)
        self.setup = Settings(data_folder=self.data_folder)
        self.cb = Callbacks()
        self.ssp = None

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
        logger.debug("data reader: %s" % reader)
        logger.debug("import path: %s" % data_path)
        success = reader.read(data_path=data_path, settings=self.setup, callbacks=self.cb)
        if not success:
            raise RuntimeError("Error using %s reader for file: %s"
                               % (reader.desc, data_path))
        self.ssp = reader.ssp

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

    # --- repr

    def __repr__(self):
        msg = "%s" % super(Project, self).__repr__()
        msg += "%s" % self.setup
        return msg
