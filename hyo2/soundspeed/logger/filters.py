import logging

logger = logging.getLogger(__name__)


class ServerFilter(logging.Filter):
    def filter(self, record):
        # print(record.name, record.levelname)
        if record.name.startswith('hyo.ssp.server'):
            return True
        return False


class NotServerFilter(logging.Filter):
    def filter(self, record):
        # print(record.name, record.levelname)
        if record.name.startswith('hyo.ssp.server'):
            return False
        return True
