import sys
import traceback
import logging

from PySide2 import QtCore, QtWidgets

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.app.app_style import AppStyle

set_logging(ns_list=["hyo2.abc", "hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings",
                     "hyo2.surveydatamonitor"])
logger = logging.getLogger(__name__)


def qt_custom_handler(error_type: QtCore.QtMsgType, error_context: QtCore.QMessageLogContext, message: str):

    logger.info("Qt error: %s [%s, %s:%s:%d, v.%s] -> %s"
                % (error_type, error_context.category, error_context.file, error_context.function,
                   error_context.line, error_context.version, message))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMessageHandler(qt_custom_handler)


def gui():
    """Create the application and show the Sound Speed Manager gui"""
    from hyo2.soundspeedmanager.mainwin import MainWin

    app = QtWidgets.QApplication([])
    app.setStyleSheet(AppStyle.load_stylesheet())

    main_win = MainWin()
    sys.excepthook = main_win.exception_hook  # install the exception hook
    main_win.show()
    main_win.do()

    sys.exit(app.exec_())
