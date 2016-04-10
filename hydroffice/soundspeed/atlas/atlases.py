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
        self.data_folder = os.path.join(self.prj.data_folder, "atlases")
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        # available atlases
        self.rtofs = Rtofs(self.data_folder)
        self.woa09 = Woa09(self.data_folder)
        self.woa13 = Woa13(self.data_folder)

    @property
    def woa09_folder(self):
        return self.woa09.folder

    @property
    def woa13_folder(self):
        return self.woa13.folder

    @property
    def rtofs_folder(self):
        return self.rtofs.folder

    def __repr__(self):
        msg = "<Atlases>\n"
        msg += "%s" % self.rtofs
        msg += "%s" % self.woa09
        msg += "%s" % self.woa13
        return msg
