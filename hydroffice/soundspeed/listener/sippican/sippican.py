from __future__ import absolute_import, division, print_function, unicode_literals

import socket
import operator
import logging
import functools
from threading import Thread, Event
import time

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.listener.abstract import AbstractListener
from hydroffice.soundspeed.formats.readers import sippican


class Sippican(AbstractListener):
    """Sippicanlistener"""

    def __init__(self, port, prj, timeout=1, ip="0.0.0.0", target=None, name="Sippican"):
        super(Sippican, self).__init__(port=port, ip=ip, timeout=timeout,
                                       target=target, name=name)
        self.desc = "Sippican"
        self.prj = prj

        self.new_ssp = Event()

        self.ssp = None

    def __repr__(self):
        msg = "%s" % super(Sippican, self).__repr__()
        # msg += "  <has data loaded: %s>\n" % self.has_data_loaded
        return msg

    def parse(self):
        logger.debug("parse")
        # self.ssp = sippican.Sippican()
        self.data = None
        self.new_ssp.set()