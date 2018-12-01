from hyo2.soundspeed.logging import test_logging

import logging
import time
from multiprocessing import Pipe

from hyo.sis.lib.process import SisProcess

logger = logging.getLogger()


def main():

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


if __name__ == "__main__":
    main()
