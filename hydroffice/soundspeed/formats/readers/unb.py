from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)


from ..abstract import AbstractReader


class Unb(AbstractReader):
    """UNB reader"""

    def __init__(self):
        super(Unb, self).__init__()
