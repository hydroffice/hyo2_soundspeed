from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)


from ..abstract import AbstractReader


class Seabird(AbstractReader):
    """Seabird reader"""

    def __init__(self):
        super(Seabird, self).__init__()
        self._ext.add('cnv')

    def read(self, data_path):
        pass

    def _parse_header(self):
        pass

    def _parse_body(self):
        pass