from __future__ import absolute_import, division, print_function, unicode_literals

import time
import multiprocessing

from hydroffice.sis.process import SisProcess

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)


def main():
    # multiprocessing.log_to_stderr(logging.DEBUG)

    print("*** sis process ***")
    p = SisProcess()
    p.start()

    count = 0
    while True:

        if not p.is_alive():
            break

        if count == 3:
            print("trigger termination")
            p.stop()

        count += 1
        time.sleep(0.5)

    print("alive: %s" % p.is_alive())
    print('%s.exitcode = %s' % (p.name, p.exitcode))  # <0: killed with signal; >0: exited with error

if __name__ == "__main__":
    main()
