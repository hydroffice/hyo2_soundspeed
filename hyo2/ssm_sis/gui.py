import sys
import traceback
import logging

from PySide2 import QtCore, QtWidgets

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.app.app_style import AppStyle

set_logging(ns_list=["hyo2.abc", "hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings",
                     "hyo2.surveydatamonitor", "hyo2.ssm_sis",])
logger = logging.getLogger(__name__)


def qt_custom_handler(error_type: QtCore.QtMsgType, error_context: QtCore.QMessageLogContext, message: str):

    logger.info("Qt error: %s [%s, %s:%s:%d, v.%s] -> %s"
                % (error_type, error_context.category, error_context.file, error_context.function,
                   error_context.line, error_context.version, message))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMessageHandler(qt_custom_handler)


def gui():
    """Create the application and show the SSM-SIS gui"""
    from hyo2.ssm_sis.mainwin import MainWin

    app = QtWidgets.QApplication([])
    app.setStyleSheet(AppStyle.load_stylesheet())

    main_win = MainWin()
    main_win.show()

    sys.exit(app.exec_())
