import sys
import traceback
import logging

from PySide6 import QtCore, QtWidgets

from hyo2.abc2.app.app_style import AppStyle
from hyo2.abc2.lib.logging import set_logging

set_logging(ns_list=["hyo2.abc2", "hyo2.ssm2", "hyo2.sdm2"])
logger = logging.getLogger(__name__)


def qt_custom_handler(error_type: QtCore.QtMsgType, error_context: QtCore.QMessageLogContext, message: str):
    if "Cannot read property 'id' of null" in message:
        return
    if "GLImplementation: desktop" in message:
        return
    logger.info("Qt error: %s [%s] -> %s"
                % (error_type, error_context, message))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMessageHandler(qt_custom_handler)


def gui():
    """Run the Sound Speed Settings gui"""
    from hyo2.ssm2.app.gui.soundspeedsettings.mainwin import MainWin
    from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

    logger.debug("Init app ...")
    app = QtWidgets.QApplication(sys.argv)
    AppStyle.apply(app=app)

    logger.debug("Init main win ...")
    lib = SoundSpeedLibrary()
    main = MainWin(lib=lib)
    main.show()

    sys.exit(app.exec_())
