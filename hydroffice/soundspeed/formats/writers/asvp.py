from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)


from ..abstract import AbstractWriter


class Asvp(AbstractWriter):
    """Kongsberg asvp writer"""

    def __init__(self):
        super(Asvp, self).__init__()
        self._ext.add('asvp')

    def write(self, data_path):
        pass
