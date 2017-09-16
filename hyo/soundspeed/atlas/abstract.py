from abc import ABCMeta, abstractmethod
import os
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.base.geodesy import Geodesy


class AbstractAtlas(metaclass=ABCMeta):
    """Common abstract atlas"""

    def __init__(self, data_folder, prj):
        self.name = self.__class__.__name__
        self.desc = "Abstract atlas"  # a human-readable description
        self.data_folder = data_folder
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

    def __repr__(self):
        msg = "  <%s>\n" % self.__class__.__name__
        msg += "      <desc: %s>\n" % self.desc
        return msg
