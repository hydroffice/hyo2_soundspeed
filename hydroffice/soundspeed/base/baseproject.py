from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)

from .. import __version__ as pkg_version
from .. import __doc__ as pkg_name
from .helper import explore_folder
from ..appdirs.appdirs import user_data_dir
from ..logging.sqlitelogging import SqliteLogging


class BaseProject(object):
    """Sound Speed base project

    It contains general functions that are not business-specific as logging and output folder.
    """

    def __init__(self, data_folder=None):
        """Initialization for the library"""

        # output data folder: where all the library data are written
        self._data_folder = data_folder
        if not self.data_folder:
            self._data_folder = user_data_dir("%s %s" % (pkg_name, pkg_version), "HydrOffice")
        if not os.path.exists(self._data_folder):  # create it if it does not exist
            os.makedirs(self._data_folder)

        self.logs = SqliteLogging(self._data_folder)

    # --- output data folder

    @property
    def data_folder(self):
        """Get the library's output data folder"""
        return self._data_folder

    @data_folder.setter
    def data_folder(self, value):
        """ Set the library's output data folder"""
        self._data_folder = value

    def open_data_folder(self):
        explore_folder(self.data_folder)

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

    # --- repr

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__
        msg += "  <data_folder:%s>\n" % self.data_folder
        msg += "  <sqlite_loggers: user %s; server %s>\n" \
               % (self.has_active_user_logger(), self.has_active_server_logger())
        return msg