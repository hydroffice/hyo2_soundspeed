import time
import logging

from hyo2.soundspeedmanager import app_info
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary
from hyo2.soundspeed.server.server import Server
from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)

lib = SoundSpeedLibrary()
lib.listen_sis()
time.sleep(3)  # for SIS emulator

server = Server(prj=lib)

success = server.check_settings()
if not success:
    exit("Issue while checking the settings")
logger.debug("Settings successfully checked")

server.start()
time.sleep(20)

server.force_send = True
time.sleep(10)

server.stop()
