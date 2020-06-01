import logging

from hyo2.soundspeedmanager import app_info
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary
from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)


# initialize the library
lib = SoundSpeedLibrary()

logger.debug(lib)

# # exploring folders
# lib.open_data_folder()
# lib.open_release_folder()
# lib.open_projects_folder()
# lib.open_atlases_folder()

ssp_list = lib.db_list_profiles()
logger.debug('profiles in db: %d' % len(ssp_list))
logger.debug('setup version: %s' % lib.setup.setup_version)

lib.close()
