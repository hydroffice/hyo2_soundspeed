import logging

from hyo2.soundspeedmanager import app_info
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary
from hyo2.abc2.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

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
