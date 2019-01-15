import sys
import traceback
import logging

from PySide2 import QtCore, QtWidgets

from hyo2.abc.app.app_style import AppStyle
from hyo2.soundspeedmanager.mainwin import MainWin

logger = logging.getLogger(__name__)


def qt_custom_handler(error_type: QtCore.QtMsgType, error_context: QtCore.QMessageLogContext, message: str):

    if error_context.category == "js":
        logger.debug("ignoring js error")
        return

    logger.info("Qt error: %s [%s, %s:%s:%d, v.%s] -> %s"
                % (error_type, error_context.category, error_context.file, error_context.function,
                   error_context.line, error_context.version, message))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMessageHandler(qt_custom_handler)


def gui():
    """Create the application and show the Sound Speed Manager gui"""

    sys.argv.append("--disable-web-security")  # temporary fix for CORS warning (QTBUG-70228)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(AppStyle.load_stylesheet())

    main_win = MainWin()
    sys.excepthook = main_win.exception_hook  # install the exception hook
    main_win.show()
    main_win.do()

    sys.exit(app.exec_())
