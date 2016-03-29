from __future__ import absolute_import, division, print_function, unicode_literals

import os
import numpy as np
import logging

logger = logging.getLogger(__name__)

from .metadata import Metadata
from .samples import Samples
from .more import More


class Profile(object):

    def __init__(self):
        self.meta = Metadata()
        self.data = Samples()
        self.more = More()

    def __repr__(self):
        msg = "<Profile>\n"
        msg += "%s" % self.meta
        msg += "%s" % self.data
        msg += "%s" % self.more
        return msg

    def resize(self, count):
        self.data.resize(count)
        self.more.resize(count)
