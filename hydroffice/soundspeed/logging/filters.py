from __future__ import absolute_import, division, print_function, unicode_literals

import logging

logger = logging.getLogger(__name__)


class ServerFilter(logging.Filter):
    def filter(self, record):
        # print(record.name, record.levelname)
        if record.name.startswith('hydroffice.ssp.server'):
            return True
        return False


class NotServerFilter(logging.Filter):
    def filter(self, record):
        # print(record.name, record.levelname)
        if record.name.startswith('hydroffice.ssp.server'):
            return False
        return True