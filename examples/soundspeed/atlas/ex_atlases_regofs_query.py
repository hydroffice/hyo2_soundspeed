import time
from datetime import datetime, timezone
import logging
from enum import IntEnum
from PySide6 import QtWidgets

from hyo2.abc2.app.qt_progress import QtProgress
from hyo2.abc2.lib.logging import set_logging
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary
from hyo2.ssm2.app.gui.soundspeedmanager.qt_callbacks import QtCallbacks
from hyo2.ssm2.lib.atlas.regofs_model import RegOfsModel


set_logging(ns_list=["hyo2.abc2", "hyo2.ssm2"])

logger = logging.getLogger(__name__)

app = QtWidgets.QApplication([])
mw = QtWidgets.QMainWindow()
mw.show()

lib = SoundSpeedLibrary(progress=QtProgress(parent=mw), callbacks=QtCallbacks(parent=mw))

for model in RegOfsModel:
    logger.info(f"Model: {model.name} ...")

    has_model = model.lib_func_has_model(lib=lib)
    download_model = model.lib_func_download_model(lib=lib)
    query = model.lib_func_query(lib=lib)

    if not has_model():
        download_model()
    logger.debug(f"has model: {has_model()}")

    test = model.test

    start_time = time.time()
    logger.info(f"profiles:\n%s" % query(lat=test[0], lon=test[1], datestamp=test[2]))
    logger.info("execution time: %.3f s" % (time.time() - start_time))

    logger.info(f"Model: {model.name} ... DONE")
