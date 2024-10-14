import os
import logging

from hyo2.ssm2.lib.atlas.woa09 import Woa09
from hyo2.ssm2.lib.atlas.woa13 import Woa13
from hyo2.ssm2.lib.atlas.woa18 import Woa18
from hyo2.ssm2.lib.atlas.rtofs import Rtofs
from hyo2.ssm2.lib.atlas.regofsonline import RegOfsOnline
from hyo2.ssm2.lib.atlas.regofsoffline import RegOfsOffline

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
        if (self.prj.setup.custom_woa13_folder is None) or (self.prj.setup.custom_woa13_folder == ""):
            woa13_folder = os.path.join(self._atlases_folder, "woa13")
        else:
            if os.path.exists(os.path.abspath(self.prj.setup.custom_woa13_folder)):
                woa13_folder = self.prj.setup.custom_woa13_folder
            else:
                woa13_folder = os.path.join(self._atlases_folder, "woa13")
        if not os.path.exists(woa13_folder):
            os.makedirs(woa13_folder)
        # logger.info("woa13 path: %s" % woa13_folder)

        # woa18
        if (self.prj.setup.custom_woa18_folder is None) or (self.prj.setup.custom_woa18_folder == ""):
            woa18_folder = os.path.join(self._atlases_folder, "woa18")
        else:
            if os.path.exists(os.path.abspath(self.prj.setup.custom_woa18_folder)):
                woa18_folder = self.prj.setup.custom_woa18_folder
            else:
                woa18_folder = os.path.join(self._atlases_folder, "woa18")
        if not os.path.exists(woa18_folder):
            os.makedirs(woa18_folder)
        # logger.info("woa18 path: %s" % woa18_folder)

        # rtofs
        rtofs_folder = os.path.join(self._atlases_folder, "rtofs")
        if not os.path.exists(rtofs_folder):
            os.makedirs(rtofs_folder)
        # logger.info("rtofs path: %s" % rtofs_folder)

        # regofs
        self._regofs_folder = os.path.join(self._atlases_folder, "regofs")
        if not os.path.exists(self._regofs_folder):
            os.makedirs(self._regofs_folder)
        # logger.info("regofs path: %s" % regofs_folder)

        # available atlases
        self.woa09 = Woa09(data_folder=woa09_folder, prj=self.prj)
        self.woa13 = Woa13(data_folder=woa13_folder, prj=self.prj)
        self.woa18 = Woa18(data_folder=woa18_folder, prj=self.prj)
        self.rtofs = Rtofs(data_folder=rtofs_folder, prj=self.prj)

        self.cbofs = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.CBOFS)
        self.dbofs = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.DBOFS)
        self.gomofs = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.GoMOFS)
        self.nyofs = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.NYOFS)
        self.sjrofs = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.SJROFS)
        self.ngofs2 = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.NGOFS2)
        self.tbofs = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.TBOFS)
        self.leofs = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.LEOFS)
        self.lmhofs = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.LMHOFS)
        self.loofs = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.LOOFS)
        self.lsofs = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.LSOFS)
        self.sscofs = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.SSCOFS)
        self.sfbofs = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.SFBOFS)
        self.wcofs = RegOfsOnline(data_folder=self._regofs_folder, prj=self.prj, model=RegOfsOnline.Model.WCOFS)

        self.offofs = RegOfsOffline(data_folder=self._regofs_folder, prj=self.prj)

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
    def woa18_folder(self):
        return self.woa18.data_folder

    @property
    def rtofs_folder(self):
        return self.rtofs.data_folder

    @property
    def regofs_folder(self):
        return self._regofs_folder

    # noinspection DuplicatedCode
    def __repr__(self):
        msg = "  <atlases>\n"
        msg += "  %s" % self.woa09
        msg += "  %s" % self.woa13
        msg += "  %s" % self.woa18
        msg += "  %s" % self.rtofs
        msg += "  %s" % self.cbofs
        msg += "  %s" % self.dbofs
        msg += "  %s" % self.gomofs
        msg += "  %s" % self.nyofs
        msg += "  %s" % self.sjrofs
        msg += "  %s" % self.ngofs2
        msg += "  %s" % self.tbofs
        msg += "  %s" % self.leofs
        msg += "  %s" % self.lmhofs
        msg += "  %s" % self.loofs
        msg += "  %s" % self.lsofs
        msg += "  %s" % self.sscofs
        msg += "  %s" % self.sfbofs
        msg += "  %s" % self.wcofs
        return msg
