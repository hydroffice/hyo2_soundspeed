from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)

from ..abstract import AbstractAtlas


class Rtofs(AbstractAtlas):
    """RTOFS atlas"""

    def __init__(self, data_folder):
        super(Rtofs, self).__init__(data_folder)
        self.name = self.__class__.__name__
        self.desc = "RTOFS"

    def is_present(self):
        """check the availability"""
        return False

    def __repr__(self):
        msg = "%s" % super(Rtofs, self).__repr__()
        return msg