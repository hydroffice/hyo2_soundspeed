import logging
from datetime import datetime

# noinspection PyUnresolvedReferences
from hyo2.abc2.lib.logging import set_logging
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

set_logging(ns_list=["hyo2.abc2", "hyo2.ssm2"])
logger = logging.getLogger(__name__)

# create a project
lib = SoundSpeedLibrary()

# set the current project name
lib.setup.current_project = 'OPR-A123-KR-22'

# retrieve previous profile
dt = datetime(year=2015, month=8, day=1, hour=12)
pk = lib.db_previous_profile_key(dt=dt)
logger.info(f"Profile key: {pk}")
if pk is not None:
    ssp = lib.db_retrieve_profile(pk=pk)
    logger.info(f"Profile: {ssp}")
