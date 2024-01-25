import time
import logging
from typing import TYPE_CHECKING

from hyo2.ssm2.lib.listener.sis.sis import Sis
from hyo2.ssm2.lib.listener.sippican.sippican import Sippican
from hyo2.ssm2.lib.listener.nmea.nmea import Nmea
from hyo2.ssm2.lib.listener.mvp.mvp import Mvp
if TYPE_CHECKING:
    from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger(__name__)


class Listeners:
    """A collection of listening processes"""

    def __init__(self, prj: 'SoundSpeedLibrary'):
        super(Listeners, self).__init__()
        # data folder
        self.prj = prj

        # available listeners
        self.sis = Sis(port=self.prj.setup.sis_listen_port,
                       timeout=self.prj.setup.sis_listen_timeout,
                       use_sis5=self.prj.setup.use_sis5)
        self.sippican = Sippican(port=self.prj.setup.sippican_listen_port, prj=prj)
        self.nmea = Nmea(port=self.prj.setup.nmea_listen_port,
                         timeout=self.prj.setup.nmea_listen_timeout)
        self.mvp = Mvp(port=self.prj.setup.mvp_listen_port, prj=prj)

    @property
    def sippican_to_process(self) -> bool:
        return self.sippican.new_ssp.is_set()

    @sippican_to_process.setter
    def sippican_to_process(self, to_process: bool) -> None:
        if not to_process:
            self.sippican.new_ssp.clear()

    @property
    def mvp_to_process(self) -> bool:
        return self.mvp.new_ssp.is_set()

    @mvp_to_process.setter
    def mvp_to_process(self, to_process: bool) -> None:
        if not to_process:
            self.mvp.new_ssp.clear()

    def listen_sis(self) -> bool:
        if not self.sis.is_alive():
            self.sis.start()
            time.sleep(0.1)
            logger.debug("start")
        return self.sis.is_alive()

    def stop_listen_sis(self) -> bool:
        if self.sis.is_alive():
            self.sis.stop()
            self.sis.join(2)
            logger.debug("stop")
        return not self.sis.is_alive()

    def listen_sippican(self) -> bool:
        if not self.sippican.is_alive():
            self.sippican.start()
            time.sleep(0.1)
            logger.debug("start")
        return self.sippican.is_alive()

    def stop_listen_sippican(self) -> bool:
        if self.sippican.is_alive():
            self.sippican.stop()
            self.sippican.join(2)
            logger.debug("stop")
        return not self.sippican.is_alive()

    def listen_nmea(self) -> bool:
        if not self.nmea.is_alive():
            self.nmea.start()
            time.sleep(0.1)
            logger.debug("start")
        return self.nmea.is_alive()

    def stop_listen_nmea(self) -> bool:
        if self.nmea.is_alive():
            self.nmea.stop()
            self.nmea.join(2)
            logger.debug("stop")
        return not self.nmea.is_alive()    

    def listen_mvp(self) -> bool:
        if not self.mvp.is_alive():
            self.mvp.start()
            time.sleep(0.1)
            logger.debug("start")
        return self.mvp.is_alive()

    def stop_listen_mvp(self) -> bool:
        if self.mvp.is_alive():
            self.mvp.stop()
            self.mvp.join(2)
            logger.debug("stop")
        return not self.mvp.is_alive()

    def stop(self) -> None:
        self.stop_listen_sis()
        self.stop_listen_sippican()
        self.stop_listen_nmea()        
        self.stop_listen_mvp()

    def __repr__(self) -> str:
        msg = "<Listeners>\n"
        msg += "%s" % self.sis
        msg += "%s" % self.sippican
        msg += "%s" % self.nmea        
        msg += "%s" % self.mvp
        return msg
