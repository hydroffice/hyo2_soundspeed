from hydroffice.soundspeed.logging.sqlitelogging import SqliteLogging

import os
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

# create
sqlite_log = SqliteLogging(output_folder=os.path.abspath(os.curdir))

# activate
sqlite_log.activate_user_db()
print("- user logging: %s" % sqlite_log.user_active)
sqlite_log.activate_server_db()
print("- server logging: %s" % sqlite_log.user_active)

# for i in range(3000):
#     logger.debug("test0")
#     logger.info("test1")
#     logger.warning("test2")
#     logger.error("test3")

# deactivate
sqlite_log.deactivate_user_db()
print("- user logging: %s" % sqlite_log.user_active)
sqlite_log.deactivate_server_db()
print("- server logging: %s" % sqlite_log.user_active)
