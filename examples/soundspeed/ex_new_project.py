from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeed.soundspeed import SoundSpeedLibrary


def main():
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

if __name__ == "__main__":
    main()
