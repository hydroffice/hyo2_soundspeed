import os
import logging

from hyo2.soundspeedmanager import app_info
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
filters = ["valeport", ]
formats = ["caris", "csv", "elac", "hypack", "ixblue", "asvp", "qps", "sonardyne", "unb", ]
data_outputs = dict()
for format in formats:
    data_outputs[format] = data_output
tests = testing.input_dict_test_files(inclusive_filters=filters)
# print(tests)

# import each identified file
for idx, testfile in enumerate(tests.keys()):

    logger.info("test: * New profile: #%03d *" % idx)

    # import
    lib.import_data(data_path=testfile, data_format=tests[testfile].name)

    # export
    # lib.export_data(data_path=data_output, data_formats=lib.name_writers)
    lib.export_data(data_paths=data_outputs, data_formats=formats)

logger.info('test: *** END ***')
