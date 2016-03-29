from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)


from ..abstract import AbstractReader


class Valeport(AbstractReader):
    """Valeport reader"""

    def __init__(self):
        super(Valeport, self).__init__()
        self._ext.add('000')
        self._ext.add('txt')

    def read(self, data_path):
        pass

    def _parse_header(self):
        pass

    def _parse_body(self):
        pass
