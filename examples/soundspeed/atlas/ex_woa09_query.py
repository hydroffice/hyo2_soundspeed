from __future__ import absolute_import, division, print_function, unicode_literals

import time
from PySide import QtGui
from datetime import datetime as dt

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary
from hydroffice.soundspeedmanager.qt_callbacks import QtCallbacks
from hydroffice.soundspeedmanager.qt_progress import QtProgress


def main():
    app = QtGui.QApplication([])  # PySide stuff (start)
    mw = QtGui.QMainWindow()
    mw.show()

    lib = SoundSpeedLibrary(progress=QtProgress(parent=mw), callbacks=QtCallbacks(parent=mw))

    tests = [
        (43.026480, -70.318824, dt.utcnow()),  # offshore Portsmouth
        # (-19.1, 74.16, dt.utcnow()),  # Indian Ocean
        # (18.2648113, 16.1761115, dt.utcnow()),  # in land -> middle of Africa
    ]

    # download the woa09 if not present
    if not lib.has_woa09():
        success = lib.download_woa09()
        if not success:
            raise RuntimeError("unable to download")
    logger.info("has woa09: %s" % lib.has_woa09())

    # logger.info("load woa09: %s" % lib.atlases.woa09.load_grids())

    # test for a few locations
    for test in tests:
        start_time = time.time()
        # just the ssp (there are also ssp_min and ssp_max)
        logger.info("woa09 profiles:\n%s" % lib.atlases.woa09.query(lat=test[0], lon=test[1], datestamp=test[2]))
        logger.info("execution time: %.3f s" % (time.time() - start_time))

    # app.exec_()  # PySide stuff (end)

if __name__ == "__main__":
    main()
