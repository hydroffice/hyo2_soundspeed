from __future__ import absolute_import, division, print_function, unicode_literals

import os
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

data_folder = helper.get_testing_data_folder()
print('\n> data folder: %s' % data_folder)

data_sub_folders = helper.get_testing_data_subfolders()
print('> sub-folders:')
for sub in data_sub_folders:
    print('  - %s' % sub)

print('\n> testing reader:')
for sub in data_sub_folders:
    for rdr in readers:
        if rdr.name.lower() == sub.lower():
            print('  - %s' % rdr.name)
            rdr_folder = os.path.join(data_folder, sub)
            test_files = [o for o in os.listdir(rdr_folder) if os.path.isfile(os.path.join(rdr_folder, o))]
            for tf in test_files:
                ret = rdr.read(os.path.join(rdr_folder, tf))
                if ret:
                    print(rdr.ssp)
