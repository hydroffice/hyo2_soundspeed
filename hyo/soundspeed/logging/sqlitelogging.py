import os
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.logging.sqlitehandler import SQLiteHandler
from hyo.soundspeed.logging.filters import NotServerFilter, ServerFilter


class SqliteLogging(object):

    def __init__(self, output_folder, user_db_file="log.user.db", server_db_file="log.server.db"):
        """Logging to Sqlite databases"""
        self.user = SQLiteHandler(db=os.path.join(output_folder, user_db_file))
        self.user.setLevel(logging.DEBUG)
        self.user.addFilter(NotServerFilter())
        self._user_active = False

        self.server = SQLiteHandler(db=os.path.join(output_folder, server_db_file))
        self.server.setLevel(logging.DEBUG)
        self.server.addFilter(ServerFilter())
        self._server_active = False

    @property
    def user_active(self):
        return self._user_active

    @property
    def server_active(self):
        return self._server_active

    def activate_user_db(self):
        logging.getLogger().addHandler(self.user)
        logger.info("START logger for user processing")
        self._user_active = True

    def deactivate_user_db(self):
        logger.info("END logger for user processing")
        logging.getLogger().removeHandler(self.user)
        self._user_active = False

    def activate_server_db(self):
        logging.getLogger().addHandler(self.server)
        logger.info("START logger for server processing")
        self._server_active = True

    def deactivate_server_db(self):
        logger.info("END logger for server processing")
        logging.getLogger().removeHandler(self.server)
        self._server_active = False
