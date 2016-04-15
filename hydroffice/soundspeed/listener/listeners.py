from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)

from .km.km import Km
# from .woa09.woa09 import Woa09
# from .woa13.woa13 import Woa13


class Listeners(object):
    """A collection of listeners"""

    def __init__(self, prj):
        # data folder
        self.prj = prj

        # available atlases
        self.km = Km(prj=self.prj)
        # self.woa09 = Woa09(data_folder=self.data_folder, prj=self.prj)
        # self.woa13 = Woa13(data_folder=self.data_folder, prj=self.prj)

    # @property
    # def woa09_folder(self):
    #     return self.woa09.folder
    #
    # @property
    # def woa13_folder(self):
    #     return self.woa13.folder
    #
    # @property
    # def rtofs_folder(self):
    #     return self.rtofs.folder

    def __repr__(self):
        msg = "<Listeners>\n"
        msg += "%s" % self.km
        # msg += "%s" % self.woa09
        # msg += "%s" % self.woa13
        return msg
