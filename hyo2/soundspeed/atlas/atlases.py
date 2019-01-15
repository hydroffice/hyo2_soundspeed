import os
import logging

from hyo2.soundspeed.atlas.rtofs.rtofs import Rtofs
from hyo2.soundspeed.atlas.woa09.woa09 import Woa09
from hyo2.soundspeed.atlas.woa13.woa13 import Woa13

logger = logging.getLogger(__name__)


class Atlases:
    """A collection of atlases"""

    def __init__(self, prj):
        # data folder
        self.prj = prj
        self._atlases_folder = os.path.join(self.prj.data_folder, "atlases")
        if not os.path.exists(self._atlases_folder):
            os.makedirs(self._atlases_folder)

        # rtofs
        rtofs_folder = os.path.join(self._atlases_folder, "rtofs")
        if not os.path.exists(rtofs_folder):
            os.makedirs(rtofs_folder)
        # logger.info("rtofs path: %s" % rtofs_folder)

        # woa09
        if (self.prj.setup.custom_woa09_folder is None) or (self.prj.setup.custom_woa09_folder == ""):
            woa09_folder = os.path.join(self._atlases_folder, "woa09")
        else:
            if os.path.exists(os.path.abspath(self.prj.setup.custom_woa09_folder)):
                woa09_folder = self.prj.setup.custom_woa09_folder
            else:
                woa09_folder = os.path.join(self._atlases_folder, "woa09")
        if not os.path.exists(woa09_folder):
            os.makedirs(woa09_folder)
        # logger.info("woa09 path: %s" % woa09_folder)

        # woa13
        if (self.prj.setup.custom_woa09_folder is None) or (self.prj.setup.custom_woa13_folder == ""):
            woa13_folder = os.path.join(self._atlases_folder, "woa13")
        else:
            if os.path.exists(os.path.abspath(self.prj.setup.custom_woa13_folder)):
                woa13_folder = self.prj.setup.custom_woa13_folder
            else:
                woa13_folder = os.path.join(self._atlases_folder, "woa13")
        if not os.path.exists(woa13_folder):
            os.makedirs(woa13_folder)
        # logger.info("woa13 path: %s" % woa13_folder)

        # available atlases
        self.rtofs = Rtofs(data_folder=rtofs_folder, prj=self.prj)
        self.woa09 = Woa09(data_folder=woa09_folder, prj=self.prj)
        self.woa13 = Woa13(data_folder=woa13_folder, prj=self.prj)

    @property
    def atlases_folder(self):
        return self._atlases_folder

    @property
    def woa09_folder(self):
        return self.woa09.data_folder

    @property
    def woa13_folder(self):
        return self.woa13.data_folder

    @property
    def rtofs_folder(self):
        return self.rtofs.data_folder

    def __repr__(self):
        msg = "  <atlases>\n"
        msg += "  %s" % self.rtofs
        msg += "  %s" % self.woa09
        msg += "  %s" % self.woa13
        return msg
