import os
from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeed.soundspeed import SoundSpeedLibrary
from hyo.soundspeed.base.callbacks.test_callbacks import TestCallbacks
from hyo.soundspeed.base import testing


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
    filters = ["aml", ]
    tests = testing.input_dict_test_files(inclusive_filters=filters)
    # print(tests)

    # import each identified file
    for idx, testfile in enumerate(tests.keys()):

        if idx > 4:  # FILE FILTER
            break

        logger.info("test: * New profile: #%03d *" % idx)

        # import
        lib.import_data(data_path=testfile, data_format=tests[testfile].name)
        # print(lib.cur)
        lib.plot_ssp(more=True, show=False)

        # store the current profile
        success = lib.store_data()
        logger.info("stored: %s" % success)

    from matplotlib import pyplot as plt
    plt.show()

    # retrieve all the id profiles from db
    lst = lib.db_list_profiles()
    logger.info("Profiles: %s" % len(lst))
    for p in lst:
        logger.info(p)

    # retrieve a specific profile and delete it
    ssp_pk = lst[0][0]
    ssp = lib.db_retrieve_profile(pk=ssp_pk)
    logger.info("Retrieved profile:\n%s" % ssp)
    ret = lib.delete_db_profile(pk=ssp_pk)
    logger.info("Deleted profile: %s" % ret)

    logger.info('test: *** END ***')


if __name__ == "__main__":
    main()
