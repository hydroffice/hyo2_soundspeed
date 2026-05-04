import time
from datetime import datetime as dt, UTC
import logging
from enum import IntEnum
from PySide6 import QtWidgets

from hyo2.abc2.app.qt_progress import QtProgress
from hyo2.abc2.lib.logging import set_logging
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary
from hyo2.ssm2.app.gui.soundspeedmanager.qt_callbacks import QtCallbacks


set_logging(ns_list=["hyo2.abc2", "hyo2.ssm2"])

logger = logging.getLogger(__name__)


class ModelOptions(IntEnum):
    # World Models
    WOA09 = 1
    WOA13 = 2
    RTOFS = 3
    WOA18 = 4


# Choose Model
switch = ModelOptions.RTOFS  # Choose a ModelOptions Value to test

app = QtWidgets.QApplication([])  # PySide stuff (start)
mw = QtWidgets.QMainWindow()
mw.show()

lib = SoundSpeedLibrary(progress=QtProgress(parent=mw), callbacks=QtCallbacks(parent=mw))

# Choose test location
tests = [

    (-19.1, 74.17, dt.now(UTC))               # Indian Ocean
    # (72.852028, -67.315431, dt.now(UTC))      # Baffin Bay
    # (18.2648113, 16.1761115, dt.now(UTC))     # in land -> middle of Africa
    # (39.725989, -104.967745, dt.now(UTC))     # in land -> Denver, CO
]

if switch is ModelOptions.WOA09:

    # download the woa09 if not present
    if not lib.has_woa09():
        success = lib.download_woa09()
        if not success:
            raise RuntimeError("unable to download")
    logger.info("has WOA09: %s" % lib.has_woa09())

elif switch is ModelOptions.WOA13:

    # download the woa13 if not present
    if not lib.has_woa13():
        success = lib.download_woa13()
        if not success:
            raise RuntimeError("unable to download")
    logger.info("has WOA13: %s" % lib.has_woa13())

elif switch is ModelOptions.WOA18:

    # download the woa18 if not present
    if not lib.has_woa18():
        success = lib.download_woa18()
        if not success:
            raise RuntimeError("unable to download")
    logger.info("has WOA18: %s" % lib.has_woa18())

elif switch is ModelOptions.RTOFS:

    # download the current-time rtofs
    if not lib.has_rtofs():
        lib.download_rtofs()
    logger.info("has RTOFS: %s" % lib.has_rtofs())

else:
    raise RuntimeError("invalid switch value: %s" % switch)

# test for a few locations
for test in tests:

    start_time = time.time()
    # just the ssp (there are also ssp_min and ssp_max)
    if switch is ModelOptions.WOA09:
        logger.info("WOA09 profiles:\n%s" % lib.atlases.woa09.query(lat=test[0], lon=test[1], dtstamp=test[2]))
    elif switch is ModelOptions.WOA13:
        logger.info("WOA13 profiles:\n%s" % lib.atlases.woa13.query(lat=test[0], lon=test[1], dtstamp=test[2]))
    elif switch is ModelOptions.WOA18:
        logger.info("WOA18 profiles:\n%s" % lib.atlases.woa18.query(lat=test[0], lon=test[1], dtstamp=test[2]))
    elif switch is ModelOptions.RTOFS:
        logger.info("RTOFS profiles:\n%s" % lib.atlases.rtofs.query(lat=test[0], lon=test[1], dtstamp=test[2]))
    else:
        raise RuntimeError("invalid switch value: %s" % switch)
    logger.info("execution time: %.3f s" % (time.time() - start_time))

app.exec()  # no need to actually run the message loop
