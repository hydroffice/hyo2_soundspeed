from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)

from . import __version__ as pkg_version
from . import __doc__ as pkg_name
from .helper import explore_folder
from .appdirs.appdirs import user_data_dir


class Project(object):
    """Sound Speed project"""

    def __init__(self, data_folder=None):
        """Initialization for the library"""

        # output data folder: where all the library data are written
        self._data_folder = data_folder
        if not self.data_folder:
            self._data_folder = user_data_dir("%s %s" % (pkg_name, pkg_version), "HydrOffice")
        if not os.path.exists(self._data_folder):  # create it if it does not exist
            os.makedirs(self._data_folder)

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

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__
        msg += "  <data_folder:%s>" % self.data_folder
        return msg
