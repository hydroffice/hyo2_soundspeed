import os
import logging

from hyo2.soundspeed.logger.sqlitelogging import SqliteLogging
from hyo2.soundspeed.base.testing import SoundSpeedTesting

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# create
data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
testing = SoundSpeedTesting(root_folder=data_folder)
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
