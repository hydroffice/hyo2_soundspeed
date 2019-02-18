import time
import logging

from hyo2.soundspeed.listener.sis.sis5 import Sis5

logging.basicConfig(level=logging.DEBUG)
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
