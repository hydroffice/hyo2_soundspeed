from __future__ import absolute_import, division, print_function, unicode_literals

from hydroffice.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

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

    # - aux methods
    print("\npairing readers and folders (no filters):")
    pair_dict = testing.pair_readers_and_folders(folders=testing.input_data_sub_folders())
    for fmt in pair_dict:
        print("- %s: %s" % (fmt, pair_dict[fmt]))

    print("\npairing readers and folders (with valeport filter):")
    filters = ["valeport", ]
    pair_dict = testing.pair_readers_and_folders(folders=testing.input_data_sub_folders(),
                                                 inclusive_filters=filters)
    for fmt in pair_dict:
        print("- %s: %s" % (fmt, pair_dict[fmt]))

    print("\ngetting dict of files and readers:")
    files_dict = testing.dict_test_files(data_folder=testing.input_data_folder(),
                                         pairs=pair_dict)
    for fid in files_dict:
        print("- %s: %s" % (fid, files_dict[fid]))

    print("\ngetting dict of input files and readers:")
    input_dict = testing.input_dict_test_files()
    for fid in input_dict:
        print("- %s: %s" % (fid, input_dict[fid]))


if __name__ == "__main__":
    main()
