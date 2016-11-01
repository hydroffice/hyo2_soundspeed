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



    # print(lib)

    # # exploring folders
    # lib.open_data_folder()
    # lib.open_release_folder()
    # lib.open_projects_folder()
    # lib.open_atlases_folder()

    lib.close()

if __name__ == "__main__":
    main()
