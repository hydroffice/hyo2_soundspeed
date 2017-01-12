from __future__ import absolute_import, division, print_function, unicode_literals

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary


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
