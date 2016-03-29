from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)


from ..abstract import AbstractReader


class Digibar(AbstractReader):
    """Digibar reader"""

    def __init__(self):
        super(Digibar, self).__init__()
