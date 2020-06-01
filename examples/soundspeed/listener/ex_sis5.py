import time
import logging

from hyo2.soundspeed.listener.sis.sis5 import Sis5
from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)

listen_ip = "224.1.20.40"
listen_port = 6020
datagrams = [b'#MRZ', b'#SPO', b'#SVP']

sis5 = Sis5(ip=listen_ip, port=listen_port, datagrams=datagrams, timeout=10)

if not sis5.is_alive():
    sis5.start()

    time.sleep(0.1)
    logger.debug("start")

time.sleep(100)

if sis5.is_alive():
    sis5.stop()
    sis5.join(2)
    logger.debug("stop")


logger.debug("STOP: %s" % sis5.is_alive())
