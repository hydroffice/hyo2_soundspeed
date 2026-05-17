import logging
import time

from PySide6 import QtWidgets

# noinspection PyUnresolvedReferences
from hyo2.abc2.app.qt_progress import QtProgress
# noinspection PyUnresolvedReferences
from hyo2.abc2.lib.logging import set_logging
# noinspection PyUnresolvedReferences
from hyo2.ssm2.app.gui.soundspeedmanager.qt_callbacks import QtCallbacks
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.atlas.abstract import AbstractAtlas
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.atlas.regofs_model import RegOfsModel
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

set_logging(ns_list=["hyo2.abc2", "hyo2.ssm2"])

logger = logging.getLogger(__name__)

interactive = False
models: list[RegOfsModel] = list(RegOfsModel)
skip_models: tuple[RegOfsModel, ...] = RegOfsModel.skip_models()

app = QtWidgets.QApplication([])
mw = QtWidgets.QMainWindow()
mw.show()

lib = SoundSpeedLibrary(progress=QtProgress(parent=mw), callbacks=QtCallbacks(parent=mw))

for model in models:
    logger.info(f"Model: {model.name} ...")

    if model in RegOfsModel.skip_models():
        logger.info(f"Model: {model.name} ... SKIP")
        continue

    has_model = model.lib_func_has_model(lib=lib)
    download_model = model.lib_func_download_model(lib=lib)
    query = model.lib_func_query(lib=lib)

    if not has_model():
        download_model()
    logger.debug(f"has model: {has_model()}")

    test = model.test

    start_time = time.time()
    if interactive:
        # ask user for location and timestamp
        model.lib_func_retrieve(lib=lib)()
        ssp = lib.ssp
    else:
        ssp = query(lat=test[0], lon=test[1], datestamp=test[2])
    logger.info(f"profiles:\n{ssp}")
    logger.info("execution time: %.3f s" % (time.time() - start_time))

    logger.info(f"Model: {model.name} ... DONE")
