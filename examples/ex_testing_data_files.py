from __future__ import absolute_import, division, print_function, unicode_literals

import os
from matplotlib import pyplot as plt
from hydroffice.soundspeed import helper
from hydroffice.soundspeed.formats import readers

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

# retrieve data folder
data_folder = helper.get_testing_data_folder()
logger.info('data folder: %s' % data_folder)

# test specific reader
logger.info('testing reader:')
data_sub_folders = helper.get_testing_data_subfolders()
for sub in data_sub_folders:  # retrieve the format-specific sub-folders
    for rdr in readers:

        # if rdr.name.lower() != 'kongsberg':
        #     continue

        if rdr.name.lower() != sub.lower():  # skip not matching readers
            continue
        logger.info('- %s [%s]' % (rdr.name, ','.join(rdr.ext)))

        # retrieve test files
        rdr_folder = os.path.join(data_folder, sub)
        test_files = list()
        for r, dirs, files in os.walk(rdr_folder):
            [test_files.append(os.path.join(r, tf)) for tf in files]

        # use test files
        for tf in test_files:

            # check the extension
            ext = tf.split('.')[-1].lower()
            if ext not in rdr.ext:
                continue

            # try to read the file
            logger.info('  . %s' % tf)
            ret = rdr.read(os.path.join(rdr_folder, tf))
            if ret:
                logger.info(rdr.ssp)
                rdr.ssp.debug_plot(more=True)

plt.show()
