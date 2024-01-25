import logging
import os

from hyo2.abc2.lib.logging import set_logging
from hyo2.ssm2.lib.base.callbacks.fake_callbacks import FakeCallbacks
from hyo2.ssm2.lib.base.testing import SoundSpeedTesting
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

set_logging(ns_list=["hyo2.abc2", "hyo2.ssm2"])

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
