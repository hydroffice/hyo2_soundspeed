import logging

from hyo2.abc2.lib.logging import set_logging
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

set_logging(ns_list=["hyo2.abc2", "hyo2.ssm2"])

logger = logging.getLogger(__name__)

# initialize the library
lib = SoundSpeedLibrary()

prj_list = lib.list_projects()
logger.debug("projects: %s" % len(prj_list))
for prj in prj_list:
    logger.debug('- %s' % prj)

lib.current_project = "test2"

ssp_list = lib.db_list_profiles()
logger.debug('profiles in db: %d' % len(ssp_list))

lib.close()
