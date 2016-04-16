from __future__ import absolute_import, division, print_function, unicode_literals

import os
import time
from multiprocessing import Queue
import logging

logger = logging.getLogger(__name__)

from .sis.sis import Sis
from .sippican.sippican import Sippican
from .mvp.mvp import Mvp


class Listeners(object):
    """A collection of listening processes"""

    def __init__(self, prj):
        super(Listeners, self).__init__()
        # data folder
        self.prj = prj

        # available listeners
        self.sis = Sis(port=self.prj.setup.sis_listen_port, datagrams=[0x50, 0x52, 0x55, 0x58],
                       timeout=self.prj.setup.sis_listen_timeout)
        self.sippican = Sippican(port=self.prj.setup.sippican_listen_port)
        self.mvp = Mvp(port=self.prj.setup.mvp_listen_port)

    def listen_sis(self):
        if not self.sis.is_alive():
            self.sis.start()
            time.sleep(0.1)
        return self.sis.is_alive()

    def stop_listen_sis(self):
        logger.debug("stop")
        if self.sis.is_alive():
            self.sis.stop()
            self.sis.join(2)
        return not self.sis.is_alive()

    def listen_sippican(self):
        if not self.sippican.is_alive():
            self.sippican.start()
            time.sleep(0.1)
        return self.sippican.is_alive()

    def stop_listen_sippican(self):
        logger.debug("stop")
        if self.sippican.is_alive():
            self.sippican.stop()
            self.sippican.join(2)
        return not self.sippican.is_alive()

    def listen_mvp(self):
        if not self.mvp.is_alive():
            self.mvp.start()
            time.sleep(0.1)
        return self.mvp.is_alive()

    def stop_listen_mvp(self):
        logger.debug("stop")
        if self.mvp.is_alive():
            self.mvp.stop()
            self.mvp.join(2)
        return not self.mvp.is_alive()

    def stop(self):
        self.stop_listen_sis()
        self.stop_listen_sippican()
        self.stop_listen_mvp()

    def __repr__(self):
        msg = "<Listeners>\n"
        msg += "%s" % self.sis
        msg += "%s" % self.sippican
        msg += "%s" % self.mvp
        return msg
