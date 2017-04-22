import time
from PySide import QtGui
from datetime import datetime as dt

from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeed.soundspeed import SoundSpeedLibrary
from hyo.soundspeedmanager.qt_callbacks import QtCallbacks
from hyo.soundspeedmanager.qt_progress import QtProgress


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

    # download the woa13 if not present
    if not lib.has_woa13():
        success = lib.download_woa13()
        if not success:
            raise RuntimeError("unable to download")
    logger.info("has woa09: %s" % lib.has_woa13())

    # logger.info("load woa13: %s" % lib.atlases.woa13.load_grids())

    # test for a few locations
    for test in tests:
        start_time = time.time()
        # just the ssp (there are also ssp_min and ssp_max)
        logger.info("woa13 profiles:\n%s" % lib.atlases.woa13.query(lat=test[0], lon=test[1], datestamp=test[2]))
        logger.info("execution time: %.3f s" % (time.time() - start_time))

    # app.exec_()  # PySide stuff (end)

if __name__ == "__main__":
    main()
