from hydroffice.soundspeed.logging.sqlitelogging import SqliteLogging
from hydroffice.soundspeed.base import testing

import os
from hydroffice.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

# create
sqlite_log = SqliteLogging(output_folder=testing.output_data_folder())

# activate
sqlite_log.activate_user_db()
print("- user logging: %s" % sqlite_log.user_active)
sqlite_log.activate_server_db()
print("- server logging: %s" % sqlite_log.user_active)

for i in range(100):
    logger.debug("test0")
    logger.info("test1")
    logger.warning("test2")
    logger.error("test3")

# deactivate
sqlite_log.deactivate_user_db()
print("- user logging: %s" % sqlite_log.user_active)
sqlite_log.deactivate_server_db()
print("- server logging: %s" % sqlite_log.user_active)
