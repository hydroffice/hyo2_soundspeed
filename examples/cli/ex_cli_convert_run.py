import logging
import os
import sys

from hyo2.abc2.lib.testing import Testing
from hyo2.ssm2.app.gui.soundspeedmanager.main import main

logger = logging.getLogger(__name__)
testing = Testing()

use_folder = True

input_path = testing.input_test_files(".csv", subfolder="nemo")[0]
if use_folder:
    input_path = os.path.dirname(input_path)

logger.debug("initial argv: %s" % sys.argv)
sys.argv.append("convert")
sys.argv.append(input_path)
sys.argv.append(testing.output_data_folder())
sys.argv.append("--input_format")
sys.argv.append("nemo")
sys.argv.append("--output_format")
sys.argv.append("asvp/ssp")
sys.argv.append("--save_to_database")
sys.argv.append("--retrieve_temperature_salinity")
sys.argv.append("--extend_profile")
logger.debug("passed argv: %s" % sys.argv)

main()
