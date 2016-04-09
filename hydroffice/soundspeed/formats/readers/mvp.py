from __future__ import absolute_import, division, print_function, unicode_literals

import logging

logger = logging.getLogger(__name__)


from .abstract import AbstractReader
from ...profile.dicts import Dicts
from ...base.callbacks import Callbacks


class Mvp(AbstractReader):
    """MVP reader"""

    def __init__(self):
        super(Mvp, self).__init__()

    def read(self, data_path, settings, callbacks=Callbacks()):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        pass

    def _parse_body(self):
        pass