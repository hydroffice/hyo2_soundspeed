import os
import logging

from hyo2.soundspeed.atlas.woa09 import Woa09
from hyo2.soundspeed.atlas.woa13 import Woa13
from hyo2.soundspeed.atlas.rtofs import Rtofs
from hyo2.soundspeed.atlas.regofs import RegOfs

logger = logging.getLogger(__name__)


class Atlases:
    """A collection of atlases"""

    def __init__(self, prj):
        # data folder
        self.prj = prj
        self._atlases_folder = os.path.join(self.prj.data_folder, "atlases")
        if not os.path.exists(self._atlases_folder):
            os.makedirs(self._atlases_folder)

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

        # rtofs
        rtofs_folder = os.path.join(self._atlases_folder, "rtofs")
        if not os.path.exists(rtofs_folder):
            os.makedirs(rtofs_folder)
        # logger.info("rtofs path: %s" % rtofs_folder)

        # regofs
        regofs_folder = os.path.join(self._atlases_folder, "regofs")
        if not os.path.exists(regofs_folder):
            os.makedirs(regofs_folder)
        # logger.info("regofs path: %s" % regofs_folder)

        # available atlases
        self.woa09 = Woa09(data_folder=woa09_folder, prj=self.prj)
        self.woa13 = Woa13(data_folder=woa13_folder, prj=self.prj)
        self.rtofs = Rtofs(data_folder=rtofs_folder, prj=self.prj)

        self.cbofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.CBOFS)
        self.dbofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.DBOFS)
        self.gomofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.GoMOFS)
        self.nyofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.NYOFS)
        self.sjrofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.SJROFS)
        self.ngofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.NGOFS)
        self.tbofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.TBOFS)
        self.leofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.LEOFS)
        self.lhofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.LHOFS)
        self.lmofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.LMOFS)
        self.loofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.LOOFS)
        self.lsofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.LSOFS)
        self.creofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.CREOFS)
        self.sfbofs = RegOfs(data_folder=regofs_folder, prj=self.prj, model=RegOfs.Model.SFBOFS)

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

    @property
    def cbofs_folder(self):
        return self.cbofs.data_folder

    @property
    def dbofs_folder(self):
        return self.dbofs.data_folder

    @property
    def gomofs_folder(self):
        return self.gomofs.data_folder

    @property
    def nyofs_folder(self):
        return self.nyofs.data_folder

    def sjrofs_folder(self):
        return self.sjrofs.data_folder

    @property
    def ngofs_folder(self):
        return self.ngofs.data_folder

    @property
    def tbofs_folder(self):
        return self.tbofs.data_folder

    @property
    def leofs_folder(self):
        return self.leofs.data_folder

    @property
    def lhofs_folder(self):
        return self.lhofs.data_folder

    @property
    def lmofs_folder(self):
        return self.lmofs.data_folder

    @property
    def loofs_folder(self):
        return self.loofs.data_folder

    @property
    def lsofs_folder(self):
        return self.lsofs.data_folder

    @property
    def creofs_folder(self):
        return self.creofs.data_folder

    @property
    def sfbofs_folder(self):
        return self.sfbofs.data_folder

    def __repr__(self):
        msg = "  <atlases>\n"
        msg += "  %s" % self.woa09
        msg += "  %s" % self.woa13
        msg += "  %s" % self.rtofs
        msg += "  %s" % self.cbofs
        msg += "  %s" % self.dbofs
        msg += "  %s" % self.gomofs
        msg += "  %s" % self.nyofs
        msg += "  %s" % self.sjrofs
        msg += "  %s" % self.ngofs
        msg += "  %s" % self.tbofs
        msg += "  %s" % self.leofs
        msg += "  %s" % self.lhofs
        msg += "  %s" % self.lmofs
        msg += "  %s" % self.loofs
        msg += "  %s" % self.lsofs
        msg += "  %s" % self.creofs
        msg += "  %s" % self.sfbofs
        return msg
