from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)


from ..abstract import AbstractWriter


class Elac(AbstractWriter):
    """Elac writer"""

    def __init__(self):
        super(Elac, self).__init__()
        self._ext.add('sva')
