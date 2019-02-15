import logging
import time
from multiprocessing import Pipe, freeze_support

from hyo2.sis4.lib.process import SisProcess


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

test_files = [
    r"C:\Users\gmasetti\Google Drive\Mike\data\all\sally_ride\0000_20170104_185019_SallyRide.all",
    r"C:\Users\gmasetti\Google Drive\Mike\data\kmall\5deeps\0008_20181215_033617_PressureDrop.kmall",
    r"C:\Users\gmasetti\Google Drive\Mike\data\kmall\5deeps\0009_20181215_040502_PressureDrop.kmall",
    r"C:\Users\gmasetti\Google Drive\Mike\data\kmall\5deeps\0010_20181215_042649_PressureDrop.kmall",
]

if __name__ == '__main__':
    freeze_support()

    ip_out = "localhost"
    port_out = 26103

    logger.debug("starting SIS4 process ...")
    parent_conn, child_conn = Pipe()
    p = SisProcess(conn=child_conn, ip_out=ip_out, port_out=port_out)
    p.set_files(test_files)
    p.start()

    count = 0
    while True:

        if not p.is_alive():
            break

        if count == 10:
            logger.debug("trigger termination")
            p.stop()

        count += 1
        logger.debug(" ... %d ..." % count)
        time.sleep(0.5)

    logger.debug("SIS process is alive? %s" % p.is_alive())
    logger.debug('%s.exitcode = %s' % (p.name, p.exitcode))  # <0: killed with signal; >0: exited with error
