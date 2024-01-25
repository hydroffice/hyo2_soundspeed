import logging
import time

from hyo2.abc2.lib.logging import set_logging
from hyo2.ssm2.lib.server.server import Server
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

set_logging(ns_list=["hyo2.abc2", "hyo2.ssm2"])

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
