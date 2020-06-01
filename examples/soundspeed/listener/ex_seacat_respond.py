import os
import logging

from hyo2.soundspeed.listener.seacat.seacat_emulator import raw_capture
from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)

p = os.path.join(os.path.split(os.path.abspath(__file__))[0], "seacat_capture.txt")
raw_capture(p)
