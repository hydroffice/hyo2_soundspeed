from __future__ import absolute_import, division, print_function, unicode_literals

import os
from hydroffice.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary
from hydroffice.soundspeed.base.callbacks.test_callbacks import TestCallbacks
from hydroffice.soundspeed.base import testing


def pair_reader_and_folder(folders, readers):
    """Create pair of folder and reader"""

    pairs = dict()

    for folder in folders:

        folder = folder.split(os.sep)[-1]
        # logger.debug('pairing folder: %s' % folder)

        for reader in readers:

            if reader.name.lower() != 'valeport':  # READER FILTER
                continue

            if reader.name.lower() != folder.lower():  # skip not matching readers
                continue

            pairs[folder] = reader

    logger.info('pairs: %s' % pairs)
    return pairs


def list_test_files(data_input, pairs):
    """Create a dictionary of test file and reader to use with"""
    tests = dict()

    for folder in pairs.keys():

        reader = pairs[folder]
        reader_folder = os.path.join(data_input, folder)

        for root, dirs, files in os.walk(reader_folder):

            for filename in files:

                # check the extension
                ext = filename.split('.')[-1].lower()
                if ext not in reader.ext:
                    continue

                tests[os.path.join(root, filename)] = reader

    logger.info("tests (%d): %s" % (len(tests), tests))
    return tests


def main():
    # create a project with test-callbacks
    lib = SoundSpeedLibrary(callbacks=TestCallbacks())

    # set the current project name
    lib.setup.current_project = 'test'

    # retrieve data input/output folders
    data_input = testing.input_data_folder()
    logger.info('input folder: %s' % data_input)
    data_output = testing.output_data_folder()
    logger.info('output folder: %s' % data_output)

    # test readers/writers
    logger.info('test: *** START ***')
    data_sub_folders = testing.input_data_sub_folders()
    pairs = pair_reader_and_folder(folders=data_sub_folders, readers=lib.readers)
    tests = list_test_files(data_input=data_input, pairs=pairs)

    print(tests)

    # # import each identified file
    # for idx, testfile in enumerate(tests.keys()):
    #
    #     if idx > 4:  # FILE FILTER
    #         break
    #
    #     logger.info("test: * New profile: #%03d *" % idx)
    #
    #     # import
    #     lib.import_data(data_path=testfile, data_format=tests[testfile].name)
    #     # print(lib.cur)
    #     # lib.plot_ssp(more=True, show=False)
    #
    #     # store the current profile
    #     success = lib.store_data()
    #     logger.info("stored: %s" % success)
    #
    # # from matplotlib import pyplot as plt
    # # plt.show()
    #
    # # retrieve all the id profiles from db
    # lst = lib.db_list_profiles()
    # logger.info("Profiles: %s" % len(lst))
    # for p in lst:
    #     logger.info(p)
    #
    # # retrieve a specific profile and delete it
    # ssp_pk = lst[0][0]
    # ssp = lib.db_retrieve_profile(pk=ssp_pk)
    # logger.info("Retrieved profile:\n%s" % ssp)
    # ret = lib.delete_db_profile(pk=ssp_pk)
    # logger.info("Deleted profile: %s" % ret)

    logger.info('test: *** END ***')


if __name__ == "__main__":
    main()
