from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)


from ..abstract import AbstractWriter


class Kongsberg(AbstractWriter):
    """Kongsberg writer"""

    def __init__(self):
        super(Kongsberg, self).__init__()
        self._ext.add('asvp')