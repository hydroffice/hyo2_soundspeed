from datetime import datetime as dt, timedelta
import logging

from PySide2 import QtWidgets

from hyo2.abc.app.qt_progress import QtProgress
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary
from hyo2.soundspeedmanager.qt_callbacks import QtCallbacks


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = QtWidgets.QApplication([])  # PySide stuff (start)
mw = QtWidgets.QMainWindow()
mw.show()

lib = SoundSpeedLibrary(progress=QtProgress(parent=mw), callbacks=QtCallbacks(parent=mw))

tests = [
    (43.026480, -70.318824, dt.utcnow()),  # offshore Portsmouth
    (-19.1, 74.16, dt.utcnow()),  # Indian Ocean
    (18.2648113, 16.1761115, dt.utcnow()),  # in land -> middle of Africa
]

# download the woa13 if not present
if not lib.has_woa13():
    success = lib.download_woa13()
    if not success:
        raise RuntimeError("unable to download")
logger.info("has woa09: %s" % lib.has_woa13())

# logger.info("load woa13: %s" % lib.atlases.woa13.load_grids())

# test user interaction: 3 profiles (avg, min, max)
lib.retrieve_woa13()
logger.info("lib retrieve rtofs: %s" % lib.ssp)

app.exec_()  # PySide stuff (end)
