import os
import logging

from hyo2.soundspeedmanager import AppInfo
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary
from hyo2.soundspeed.base.testing import SoundSpeedTesting
from hyo2.soundspeed.base.callbacks.fake_callbacks import FakeCallbacks
from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)

# create a project with test-callbacks
lib = SoundSpeedLibrary(callbacks=FakeCallbacks())

# set the current project name
lib.setup.current_project = 'test'

data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
testing = SoundSpeedTesting(root_folder=data_folder)

# retrieve data input/output folders
data_input = testing.input_data_folder()
logger.info('input folder: %s' % data_input)
data_output = testing.output_data_folder()
logger.info('output folder: %s' % data_output)

# test readers/writers
logger.info('test: *** START ***')
filters = ["castaway", ]
formats = ["asvp", ]
data_outputs = dict()
data_outputs["asvp"] = data_output
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
