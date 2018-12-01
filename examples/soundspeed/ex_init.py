import logging

from hyo2.soundspeed.soundspeed import SoundSpeedLibrary

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# initialize the library
lib = SoundSpeedLibrary()

# print(lib)

# # exploring folders
# lib.open_data_folder()
# lib.open_release_folder()
# lib.open_projects_folder()
# lib.open_atlases_folder()

ssp_list = lib.db_list_profiles()
logger.debug('profiles in db: %d' % len(ssp_list))

logger.debug('setup version: %s' % lib.setup.setup_version)

lib.close()
