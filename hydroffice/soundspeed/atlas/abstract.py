from __future__ import absolute_import, division, print_function, unicode_literals

from abc import ABCMeta, abstractmethod, abstractproperty
import os
import logging

logger = logging.getLogger(__name__)

from ..base.geodesy import Geodesy


class AbstractAtlas(object):
    """Common abstract atlas"""

    __metaclass__ = ABCMeta

    def __init__(self, data_folder, prj):
        self.name = self.__class__.__name__
        self.desc = "Abstract atlas"  # a human-readable description
        self.data_folder = data_folder
        self._folder = None
        self.prj = prj
        self.g = Geodesy()

    @abstractmethod
    def is_present(self):
        pass

    @abstractmethod
    def query(self, lat, lon, datestamp, server_mode):
        pass

    @abstractmethod
    def download_db(self):
        pass

    @property
    def folder(self):
        """Return the db folder

        If not stored, the folder path is retrieved. It is also created in the case that does not exist"""
        if self._folder:
            return self._folder
        self._folder = os.path.join(self.data_folder, self.__class__.__name__.lower())

        if not os.path.exists(self._folder):
            os.makedirs(self._folder)

        return self._folder

    @folder.setter
    def folder(self, path):
        """Set the db folder

        If the passed path does not exists, it is created."""
        self._folder = path

        if not os.path.exists(self._folder):
            os.makedirs(self._folder)

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__
        msg += "  <desc: %s>\n" % self.desc
        msg += "  <db folder: %s>\n" % self.folder
        return msg
