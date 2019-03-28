import time
import logging

from hyo2.soundspeedmanager import app_info
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary
from hyo2.soundspeed.server.server import Server

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger()

lib = SoundSpeedLibrary()
lib.listen_sis4()
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
