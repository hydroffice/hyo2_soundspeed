from __future__ import absolute_import, division, print_function, unicode_literals

import os
from matplotlib import pyplot as plt
from hydroffice.soundspeed.base import helper
from hydroffice.soundspeed.formats import readers, writers

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)


def process_test_file(tf, rdr, rdr_folder, data_output):
    """"Process a specific test file"""

    # check the extension
    ext = tf.split('.')[-1].lower()
    if ext not in rdr.ext:
        return

    # try to read the file
    logger.info('  . %s' % tf)
    ret = rdr.read(os.path.join(rdr_folder, tf))
    if ret:
        logger.info(rdr.ssp)
        rdr.ssp.debug_plot(more=True)
        for wrt in writers:
            wrt.write(ssp=rdr.ssp, data_path=data_output)


def process_reader(sub, rdr, data_input, data_output):
    """Process all the test files for a specific reader"""
    # if rdr.name.lower() != 'elac':
    #     return

    if rdr.name.lower() != sub.lower():  # skip not matching readers
        return
    logger.info('- %s [%s]' % (rdr.name, ','.join(rdr.ext)))

    # retrieve test files
    rdr_folder = os.path.join(data_input, sub)
    test_files = list()
    for r, dirs, files in os.walk(rdr_folder):
        [test_files.append(os.path.join(r, tf)) for tf in files]

    # use test files
    for tf in test_files:
        process_test_file(tf=tf, rdr=rdr, rdr_folder=rdr_folder, data_output=data_output)
    plt.show()


def main():
    # retrieve data input/output folders
    data_input = helper.get_testing_input_folder()
    logger.info('input folder: %s' % data_input)
    data_output = helper.get_testing_output_folder()
    logger.info('output folder: %s' % data_output)

    # test specific reader
    logger.info('testing reader:')
    data_sub_folders = helper.get_testing_input_subfolders()
    for sub in data_sub_folders:  # retrieve the format-specific sub-folders
        for rdr in readers:
            process_reader(sub=sub, rdr=rdr, data_input=data_input, data_output=data_output)

if __name__ == "__main__":
    main()
