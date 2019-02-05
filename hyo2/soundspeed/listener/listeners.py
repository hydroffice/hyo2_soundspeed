import time
import logging

from hyo2.soundspeed.listener.sis.sis import Sis
from hyo2.soundspeed.listener.sippican.sippican import Sippican
from hyo2.soundspeed.listener.mvp.mvp import Mvp

logger = logging.getLogger(__name__)


class Listeners:
    """A collection of listening processes"""

    def __init__(self, prj):
        super(Listeners, self).__init__()
        # data folder
        self.prj = prj

        # available listeners
        self.sis4 = Sis(port=self.prj.setup.sis4_listen_port, datagrams=[0x50, 0x52, 0x55, 0x58],
                        timeout=self.prj.setup.sis4_listen_timeout, name="SIS4")
        self.sis5 = Sis(ip=self.prj.setup.sis5_listen_ip, port=self.prj.setup.sis5_listen_port,
                        datagrams=[b'#SPO', ],
                        timeout=self.prj.setup.sis5_listen_timeout, name="SIS5")
        self.sippican = Sippican(port=self.prj.setup.sippican_listen_port, prj=prj)
        self.mvp = Mvp(port=self.prj.setup.mvp_listen_port, prj=prj)

    @property
    def sippican_to_process(self):
        return self.sippican.new_ssp.is_set()

    @sippican_to_process.setter
    def sippican_to_process(self, to_process):
        if not to_process:
            self.sippican.new_ssp.clear()

    @property
    def mvp_to_process(self):
        return self.mvp.new_ssp.is_set()

    @mvp_to_process.setter
    def mvp_to_process(self, to_process):
        if not to_process:
            self.mvp.new_ssp.clear()

    def listen_sis4(self):
        if not self.sis4.is_alive():
            self.sis4.start()
            time.sleep(0.1)
            logger.debug("start")
        return self.sis4.is_alive()

    def stop_listen_sis4(self):
        if self.sis4.is_alive():
            self.sis4.stop()
            self.sis4.join(2)
            logger.debug("stop")
        return not self.sis4.is_alive()

    def listen_sis5(self):
        if not self.sis5.is_alive():
            self.sis5.start()
            time.sleep(0.1)
            logger.debug("start")
        return self.sis5.is_alive()

    def stop_listen_sis5(self):
        if self.sis5.is_alive():
            self.sis5.stop()
            self.sis5.join(2)
            logger.debug("stop")
        return not self.sis5.is_alive()

    def listen_sippican(self):
        if not self.sippican.is_alive():
            self.sippican.start()
            time.sleep(0.1)
            logger.debug("start")
        return self.sippican.is_alive()

    def stop_listen_sippican(self):
        if self.sippican.is_alive():
            self.sippican.stop()
            self.sippican.join(2)
            logger.debug("stop")
        return not self.sippican.is_alive()

    def listen_mvp(self):
        if not self.mvp.is_alive():
            self.mvp.start()
            time.sleep(0.1)
            logger.debug("start")
        return self.mvp.is_alive()

    def stop_listen_mvp(self):
        if self.mvp.is_alive():
            self.mvp.stop()
            self.mvp.join(2)
            logger.debug("stop")
        return not self.mvp.is_alive()

    def stop(self):
        self.stop_listen_sis4()
        self.stop_listen_sis5()
        self.stop_listen_sippican()
        self.stop_listen_mvp()

    def __repr__(self):
        msg = "<Listeners>\n"
        msg += "%s" % self.sis4
        msg += "%s" % self.sis5
        msg += "%s" % self.sippican
        msg += "%s" % self.mvp
        return msg
