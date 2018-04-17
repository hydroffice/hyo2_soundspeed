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
    filters = ["castaway", ]
    formats = ["asvp", ]
    data_outputs = [data_output, ]
    tests = testing.input_dict_test_files(inclusive_filters=filters)
    # print(tests)

    # import each identified file
    for idx, testfile in enumerate(tests.keys()):

        # # just 1 file
        # if idx != 1:
        #     continue

        logger.info("test: * New profile: #%03d *" % idx)

        # import
        lib.import_data(data_path=testfile, data_format=tests[testfile].name)

        # replace temp and salinity
        lib.replace_cur_temp_sal()

        # export
        lib.export_data(data_paths=data_outputs, data_formats=formats)

    logger.info('test: *** END ***')


if __name__ == "__main__":
    main()
