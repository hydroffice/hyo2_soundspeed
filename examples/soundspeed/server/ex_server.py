from hyo2.soundspeed.logging import test_logging

import time
import logging
logger = logging.getLogger()

from hyo2.soundspeed.server.server import Server
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary

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
