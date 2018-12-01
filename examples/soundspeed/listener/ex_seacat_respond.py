import os
import logging

from hyo2.soundspeed.listener.seacat.seacat_emulator import raw_capture

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

p = os.path.join(os.path.split(os.path.abspath(__file__))[0], "seacat_capture.txt")
raw_capture(p)
