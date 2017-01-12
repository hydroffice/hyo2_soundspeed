from __future__ import absolute_import, division, print_function, unicode_literals

from hydroffice.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary


def main():
    # initialize the library
    lib = SoundSpeedLibrary()

    # print(lib)

    # # exploring folders
    # lib.open_data_folder()
    # lib.open_release_folder()
    # lib.open_projects_folder()
    # lib.open_atlases_folder()

    ssp_list = lib.db_list_profiles()
    print('profiles in db: %d' % len(ssp_list))

    print('setup version: %s' % lib.setup.setup_version)

    lib.close()

if __name__ == "__main__":
    main()
