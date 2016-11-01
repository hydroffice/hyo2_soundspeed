from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)

from .rtofs.rtofs import Rtofs
from .woa09.woa09 import Woa09
from .woa13.woa13 import Woa13


class Atlases(object):
    """A collection of atlases"""

    def __init__(self, prj):
        # data folder
        self.prj = prj
        self._atlases_folder = os.path.join(self.prj.data_folder, "atlases")
        if not os.path.exists(self._atlases_folder):
            os.makedirs(self._atlases_folder)

        # available atlases
        self.rtofs = Rtofs(data_folder=self._atlases_folder, prj=self.prj)
        self.woa09 = Woa09(data_folder=self._atlases_folder, prj=self.prj)
        self.woa13 = Woa13(data_folder=self._atlases_folder, prj=self.prj)

    @property
    def atlases_folder(self):
        return self._atlases_folder

    @atlases_folder.setter
    def atlases_folder(self, value):
        """ Set the atlases folder"""
        self._atlases_folder = value

    @property
    def woa09_folder(self):
        return self.woa09.folder

    @woa09_folder.setter
    def woa09_folder(self, value):
        """ Set the woa09 folder"""
        self.woa09.folder = value

    @property
    def woa13_folder(self):
        return self.woa13.folder

    @woa13_folder.setter
    def woa13_folder(self, value):
        """ Set the woa13 folder"""
        self.woa13.folder = value

    @property
    def rtofs_folder(self):
        return self.rtofs.folder

    @rtofs_folder.setter
    def rtofs_folder(self, value):
        """ Set the woa09 folder"""
        self.rtofs.folder = value

    def __repr__(self):
        msg = "  <atlases>\n"
        msg += "  %s" % self.rtofs
        msg += "  %s" % self.woa09
        msg += "  %s" % self.woa13
        return msg
