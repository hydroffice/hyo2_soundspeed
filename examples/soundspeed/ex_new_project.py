import logging

from hyo2.soundspeedmanager import app_info
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
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
