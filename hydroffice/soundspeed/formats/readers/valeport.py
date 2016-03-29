from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)


from ..abstract import AbstractReader


class Valeport(AbstractReader):
    """Valeport reader"""

    def __init__(self):
        super(Valeport, self).__init__()
