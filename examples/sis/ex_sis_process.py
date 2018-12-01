import logging
import time
from multiprocessing import Pipe, freeze_support

from hyo2.sis.lib.process import SisProcess


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    freeze_support()
    logger.debug("sis process")
    parent_conn, child_conn = Pipe()
    p = SisProcess(conn=child_conn)
    p.start()

    count = 0
    while True:

        if not p.is_alive():
            break

        if count == 3:
            logger.debug("trigger termination")
            p.stop()

        count += 1
        logger.debug(" ... %d ..." % count)
        time.sleep(0.5)

    logger.debug("alive: %s" % p.is_alive())
    logger.debug('%s.exitcode = %s' % (p.name, p.exitcode))  # <0: killed with signal; >0: exited with error
