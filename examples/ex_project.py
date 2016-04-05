from __future__ import absolute_import, division, print_function, unicode_literals

from matplotlib import pyplot as plt
import os

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hydroffice.soundspeed.project import Project
from hydroffice.soundspeed.base.callbacks import TestCallbacks
from hydroffice.soundspeed.base import helper


def pair_reader_and_folder(folders, readers):
    """Create pair of folder and reader"""
    pairs = dict()
    for folder in folders:
        for reader in readers:
            if reader.name.lower() != 'valeport':  # reader filter
                continue
            if reader.name.lower() != folder.lower():  # skip not matching readers
                continue
            pairs[folder] = reader
    logger.info('pairs: %s' % pairs.keys())
    return pairs


def list_test_files(data_input, pairs):
    """Create a dictionary of test file and reader to use with"""
    tests = dict()
    for folder in pairs.keys():
        reader = pairs[folder]
        reader_folder = os.path.join(data_input, folder)

        for root, dirs, files in os.walk(reader_folder):
            for file in files:

                # check the extension
                ext = file.split('.')[-1].lower()
                if ext not in reader.ext:
                    continue

                tests[os.path.join(root, file)] = reader
    # logger.info("tests: %s" % tests)
    return tests


def main():
    # create a project
    prj = Project()
    # prj.activate_server_logger(True)
    logger.info(prj)
    # prj.open_data_folder()

    # set callbacks
    prj.set_callbacks(TestCallbacks())
    logger.info("test ask date: %s" % prj.cb.ask_date())
    logger.info("test ask location: %s, %s" % prj.cb.ask_location())

    # retrieve data input/output folders
    data_input = helper.get_testing_input_folder()
    logger.info('input folder: %s' % data_input)
    data_output = helper.get_testing_output_folder()
    logger.info('output folder: %s' % data_output)

    # test readers/writers
    logger.info('test: *** START ***')
    data_sub_folders = helper.get_testing_input_subfolders()
    pairs = pair_reader_and_folder(folders=data_sub_folders, readers=prj.readers)
    tests = list_test_files(data_input=data_input, pairs=pairs)
    for idx, test in enumerate(tests.keys()):
        if idx != 0:
            break
        logger.info("test: * NEW #%02d *" % idx)

        # import
        prj.import_data(data_path=test, data_format=tests[test].name)
        # print(prj.cur)

        # plot
        prj.plot_ssp(more=True, show=False)

        # export
        prj.export_data(data_path=data_output, data_formats=prj.name_writers)

    plt.show()

    logger.info('test: *** END ***')


if __name__ == "__main__":
    main()
