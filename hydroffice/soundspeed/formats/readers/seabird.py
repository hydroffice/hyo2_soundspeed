from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)


from ..abstract import AbstractReader


class Seabird(AbstractReader):
    """Seabird reader"""

    def __init__(self):
        super(Seabird, self).__init__()
