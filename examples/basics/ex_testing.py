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

from hydroffice.soundspeed.base import testing
from hydroffice.soundspeed.base import helper


def main():
    print("test data folder: %s" % testing.root_data_folder())
    # helper.explore_folder(testing.root_data_folder())

    # - input
    print("test input folder: %s" % testing.input_data_folder())
    # helper.explore_folder(testing.input_data_folder())
    print("test input sub-folders: %s" % testing.input_data_sub_folders())
    print("test files in input sub-folder: %s" % testing.input_test_files(testing.input_data_sub_folders()[0], '.asvp'))

    # - download
    print("test download folder: %s" % testing.download_data_folder())
    # helper.explore_folder(testing.download_data_folder())
    print("test files in download folder: %s" % testing.download_test_files(".txt"))

    # - output
    print("test output folder: %s" % testing.output_data_folder())
    # helper.explore_folder(testing.output_data_folder())


if __name__ == "__main__":
    main()
