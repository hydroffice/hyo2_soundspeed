from __future__ import absolute_import, division, print_function, unicode_literals

import os

from hydroffice.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary
from hydroffice.soundspeed.base.callbacks.test_callbacks import TestCallbacks
from hydroffice.soundspeed.base import testing


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
    filters = ["asvp", ]
    formats = ["asvp", ]
    tests = testing.input_dict_test_files(inclusive_filters=filters)
    # print(tests)

    # import each identified file
    for idx, testfile in enumerate(tests.keys()):

        # just 1 file
        if idx != 1:
            continue

        logger.info("test: * New profile: #%03d *" % idx)

        # import
        lib.import_data(data_path=testfile, data_format=tests[testfile].name)

        # replace temp and salinity
        lib.replace_cur_temp_sal()

        # export
        lib.export_data(data_path=data_output, data_formats=formats)

    logger.info('test: *** END ***')


if __name__ == "__main__":
    main()
