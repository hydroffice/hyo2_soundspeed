from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)


from .abstract import AbstractTextWriter


class Asvp(AbstractTextWriter):
    """Kongsberg asvp writer"""

    def __init__(self):
        super(Asvp, self).__init__()
        self._ext.add('asvp')

    def write(self, ssp, data_path, data_file=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.ssp = ssp
        self._write(data_path=data_path, data_file=data_file)

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _write_header(self):
        pass

    def _write_body(self):
        pass
