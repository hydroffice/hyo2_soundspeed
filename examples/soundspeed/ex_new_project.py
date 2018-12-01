import logging

from hyo2.soundspeed.soundspeed import SoundSpeedLibrary

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# initialize the library
lib = SoundSpeedLibrary()

prj_list = lib.list_projects()
print("projects: %s" % len(prj_list))
for prj in prj_list:
    print('- %s' % prj)

lib.current_project = "test2"

ssp_list = lib.db_list_profiles()
print('profiles in db: %d' % len(ssp_list))

lib.close()
